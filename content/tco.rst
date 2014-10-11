tail call optimization in CPython
=================================

:tags: de, programming, python, hack
:date: 2009-04-03 00:35:41

CPython unterstützt ja bekanntermaßen keine TCO von sich aus, weshalb
es zahlreiche mehr oder weniger schöne Hacks gibt, die das CPython
beibringen. Aber einen wirklich beeindruckenden habe ich eben in
`#python` auf Freenode gesehen, geschrieben von `habnabit`. Und zwar
wird der Bytecode geändert, ``CALL_FUNCTION`` wird zu
``JUMP_ABSOLUTE`` geändert.

**Nachtrag:** Das müsste eigentlich recht zuverlässig funktionieren,
unter verschiedenen CPython-Versionen. Für das ``CALL_FUNCTION`` müssen
die Argumente eh auf dem Stack liegen. Diese werden jetzt einfach mit
``STORE_FAST`` in die Namen geschrieben, die die Funktion entgegen nimmt,
und dann wird wieder zum Anfang der Funktion gesprungen.

.. code-block:: python

   import inspect, pprint, types, dis, struct, opcode, array
   short = struct.Struct('<H')
   
   class Label(object):
       pass
   
   class Code(object):
       @classmethod
       def from_code(cls, code_obj):
           self = cls()
           self.code_obj = code_obj
           self.names = list(code_obj.co_names)
           self.varnames = list(code_obj.co_varnames)
           self.consts = list(code_obj.co_consts)
           ret = []
           line_starts = dict(dis.findlinestarts(code_obj))
           code = code_obj.co_code
           labels = dict((addr, Label()) for addr in dis.findlabels(code))
           i, l = 0, len(code)
           extended_arg = 0
           while i < l:
               op = ord(code[i])
               if i in labels:
                   ret.append(('MARK_LABEL', labels[i]))
               if i in line_starts:
                   ret.append(('MARK_LINENO', line_starts[i]))
               i += 1
               if op >= opcode.HAVE_ARGUMENT:
                   arg, = short.unpack(code[i:i + 2])
                   arg += extended_arg
                   extended_arg = 0
                   i += 2
                   if op == opcode.EXTENDED_ARG:
                       extended_arg = arg << 16
                       continue
                   elif op in opcode.hasjabs:
                       arg = labels[arg]
                   elif op in opcode.hasjrel:
                       arg = labels[i + arg]
               else:
                   arg = None
               ret.append((opcode.opname[op], arg))
           self.code = ret
           return self
   
       def to_code(self):
           code_obj = self.code_obj
           co_code = array.array('B')
           co_lnotab = array.array('B')
           label_pos = {}
           jumps = []
           lastlineno = code_obj.co_firstlineno
           lastlinepos = 0
           for op, arg in self.code:
               if op == 'MARK_LABEL':
                   label_pos[arg] = len(co_code)
               elif op == 'MARK_LINENO':
                   incr_lineno = arg - lastlineno
                   incr_pos = len(co_code) - lastlinepos
                   lastlineno = arg
                   lastlinepos = len(co_code)
   
                   if incr_lineno == 0 and incr_pos == 0:
                       co_lnotab.append(0)
                       co_lnotab.append(0)
                   else:
                       while incr_pos > 255:
                           co_lnotab.append(255)
                           co_lnotab.append(0)
                           incr_pos -= 255
                       while incr_lineno > 255:
                           co_lnotab.append(incr_pos)
                           co_lnotab.append(255)
                           incr_pos = 0
                           incr_lineno -= 255
                       if incr_pos or incr_lineno:
                           co_lnotab.append(incr_pos)
                           co_lnotab.append(incr_lineno)
               elif arg is not None:
                   op = opcode.opmap[op]
                   if op in opcode.hasjabs or op in opcode.hasjrel:
                       jumps.append((len(co_code), arg))
                       arg = 0
                   if arg > 0xffff:
                       co_code.extend((opcode.EXTENDED_ARG,
                           (arg >> 16) & 0xff, (arg >> 24) & 0xff))
                   co_code.extend((op,
                       arg & 0xff, (arg >> 8) & 0xff))
               else:
                   co_code.append(opcode.opmap[op])
       
           for pos, label in jumps:
               jump = label_pos[label]
               if co_code[pos] in opcode.hasjrel:
                   jump -= pos + 3
               assert jump <= 0xffff
               co_code[pos + 1] = jump & 0xff
               co_code[pos + 2] = (jump >> 8) & 0xff
       
           return types.CodeType(code_obj.co_argcount, code_obj.co_nlocals, 
               code_obj.co_stacksize, code_obj.co_flags, co_code.tostring(), 
               tuple(self.consts), tuple(self.names), tuple(self.varnames), 
               code_obj.co_filename, code_obj.co_name, code_obj.co_firstlineno,
               co_lnotab.tostring(), code_obj.co_freevars, code_obj.co_cellvars)
       
       def const_idx(self, val):
           try:
               return self.consts.index(val)
           except ValueError:
               self.consts.append(val)
               return len(self.consts) - 1
   
   def tail_call(func):
       code = Code.from_code(func.func_code)
       func_name = func.__name__
       if func_name in code.varnames:
           raise SyntaxError('"%s" was found as a local variable in the function' %
               func_name)
       try:
           name_idx = code.names.index(func_name)
       except IndexError:
           raise SyntaxError('"%s" not found in function\'s global names' % 
               func_name)
       last_idx = 0
       func_start = Label()
       code.code.insert(0, ('MARK_LABEL', func_start))
       while True:
           try:
               lglobal_idx = code.code.index(('LOAD_GLOBAL', name_idx), last_idx)
           except ValueError:
               break
           
           if code.code[lglobal_idx - 1][0] != 'MARK_LINENO':
               last_idx = lglobal_idx + 1
               continue
           
           try:
               return_idx = code.code.index(('RETURN_VALUE', None), lglobal_idx)
           except ValueError:
               raise SyntaxError('"return" not found in function after "%s"' % 
                   func_name)
           
           if (return_idx != len(code.code) - 1 
                   and code.code[return_idx + 1][0] != 'MARK_LINENO'):
               last_idx = return_idx + 1
               continue
           
           if code.code[return_idx - 1][0] in ('CALL_FUNCTION_VAR', 
                   'CALL_FUNCTION_KW', 'CALL_FUNCTION_VAR_KW'):
               raise SyntaxError('calling with *a and/or **kw is unsupported')
           
           if code.code[return_idx - 1][0] != 'CALL_FUNCTION':
               last_idx = return_idx + 1
               continue
           
           if code.code[return_idx - 1][1] & 0xff00:
               raise SyntaxError('calling with keyword arguments is unsupported')
           
           arg_names, _, _, defaults = inspect.getargspec(func)
           n_args = code.code[return_idx - 1][1]
           if defaults is None:
               defaults = ()
           if n_args + len(defaults) < len(arg_names):
               raise SyntaxError('not enough arguments provided')
       
           new_bytecode = []
           if n_args < len(arg_names):
               new_bytecode.extend(
                   ('LOAD_CONST', code.const_idx(d)) 
                   for d in defaults[n_args - len(arg_names):])
           new_bytecode.extend(
               ('STORE_FAST', code.varnames.index(arg))
               for arg in reversed(arg_names))
           new_bytecode.append(('JUMP_ABSOLUTE', func_start))
           code.code[return_idx - 1:return_idx + 1] = new_bytecode
           del code.code[lglobal_idx]
       
       func.func_code = code.to_code()
       return func
   
   def factorial(n, acc=1):
       if n <= 0:
           return acc
       return factorial(n - 1, n * acc)
   
   dis.dis(factorial)
   factorial = tail_call(factorial)
   print
   dis.dis(factorial)
   
   print factorial(10000)
