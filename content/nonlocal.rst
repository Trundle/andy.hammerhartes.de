nonlocal in Python 2.x
======================

:tags: de, programming, python, hack
:date: 2011-01-11 20:43:20


In Python 3 gibt es ein neues Statement *nonlocal*, das es erlaubt,
bei verschachtelten Funktionen in der inneren Funktion einen neuen
Wert an einen lokalen Namen der äußeren Funktion zu binden. In Python
2 war es nur möglich, sich auf einen lokalen Namen der äußeren
Funktion zu beziehen.

.. note::
   :class: admonition

   Der größte Teil dieses Blogeintrags dürften
   Implementierungsdetails von CPython sein und müssen keinesfall für
   andere Python-Implementierungen gelten.

Dazu schauen wir uns als erstes eine Funktion näher an:

.. code-block:: python

   def f():
       local_name = 42

(In Python implementierte) Funktionien haben in CPython ein
sogenanntes `Code`-Objekt, das als *func_code*\ -Attribut (in Python 3
als *__code__*\ -Attribute) an die Funktion gebunden ist. In ihm sind
der Bytecode, alle verwendeten lokalen Namen und Konstanten und andere
Informationen gespeichert. All das ist direkt in Python selbst
benutzbar und sollte durchaus einmal im interaktiven Interpreter
ausprobiert werden. Der generierte Bytecode für diese Funktion sieht
wie folgt aus (die Ausgabe wurde mit dem *dis*\ -Modul von Python
gemacht):

.. code-block:: text

     2           0 LOAD_CONST               1 (42)
                 3 STORE_FAST               0 (local_name)
                 6 LOAD_CONST               0 (None)
                 9 RETURN_VALUE

Dabei ist die *2* in der ersten Spalte die Zeilennummer, die Spalte
rechts davon ist der Offset des Opcodes im Bytecode, gefolgt vom
Opcode selbst und (falls vorhanden) einem Argument. In Klammern steht
dann jeweils, was das Argument bedeutet.

Im konkreten Fall für die Funktion *f* wird also zunächst die
Konstante 1 geladen, in unserem Fall ist das 42. 42 ist hierbei im
*co_consts*\ -Attribut des Code-Objekts gespeichert. Diese 42 wird dann
auf einem internen Stack der CPython-VM abgelegt. Der nächste Opcode,
``STORE_FAST``, speichert den obersten Wert vom Stack in die lokale
Variable *local_name*. Lokale Variablen werden dabei einfach als Array
im aktuellen Frame umgesetzt (wobei dieses Array nicht von Python aus
erreichbar ist). Der Opcode speichert also einfach den Wert als ersten
Eintrag im Array. Falls jemand auf den lokalen Namensraum als Dict
zugreifen wird (etwa über *locals()* oder das *f_locals*\ -Attribut
eines Frames), wird das Dict des lokalen Namenraumes dann einfach mit
den Werten aus dem Array aktualisiert. Die benötigten Informationen,
nämlich die Namen der lokalen Variablen, finden sich im
*co_varnames*\ -Attribut des Code-Objekts.

Als nächstes wird dann die Konstante ``None`` geladen und zurückgegeben
(da eine Funktion in Python ja implizit ``None`` zurückgibt, wenn kein
anderer Rückgabewert angebeben wurde).


Als nächstes betrachten wir eine Funktion, die eine geschachtelte
Funktion zurückgibt, die einen Namen der äußeren Funktion benutzt:

.. code-block:: python

   def outer():
       outer_name = 42

       def inner():
           return outer_name
       return inner

Der Bytecode für *outer()*:

.. code-block:: text

     2           0 LOAD_CONST               1 (42)
                 3 STORE_DEREF              0 (outer_name)
   
     4           6 LOAD_CLOSURE             0 (outer_name)
                 9 BUILD_TUPLE              1
                12 LOAD_CONST               2 (<code object inner at 0x7ff7fe792cd8, file "<stdin>", line 4>)
                15 MAKE_CLOSURE             0
                18 STORE_FAST               0 (inner)
   
     6          21 LOAD_FAST                0 (inner)
                24 RETURN_VALUE

Und für *inner()*:

.. code-block:: text

     5           0 LOAD_DEREF               0 (outer_name)
                 3 RETURN_VALUE

Was hat sich geändert? Zunächst einmal fällt auf, dass in *outer()*
nicht mehr ``STORE_FAST`` zum Speichern der lokalen Variable benutzt
wird, sondern ``STORE_DEREF``. Das liegt daran, dass *outer_name* von
der inneren Funktion benutzt wird. Anstatt in einem Array wird der
Wert jetzt in einem sogenannten `Cell`-Objekt gespeicher (wobei diese
Cell-Objekte wiederum auch in einem Array im Frame gespeichert
werden). *outer_name* ist auch nicht mehr in *co_varnames*
aufgelistet, sondern in *co_cellvars*. Als nächstes wird dieses
Cell-Objekt dann auf den Stack geladen (mit ``LOAD_CLOSURE``) und in ein
Tupel gepackt (``BUILD_TUPLE``). Dieses Tupel bildet dann das
`func_closure`-Attribut der neuen Funktion *inner()*, die mit
``MAKE_CLOSURE`` erstellt wird. Schließlich wird die neu erstellte
Funktion, die sich oben auf dem Stack befindet, mit ``STORE_FAST`` an
den lokalen Namen *inner* gebunden, wieder geladen und zurückgegeben.

In *inner()* wird einfach der Wert aus dem Cell-Objekt geladen, das
aus *func_closure* genommen wird und zurückgegeben. Genau genommen
werden die Cell-Objekte aus *func_closure* zum Array der Cell-Objekte
im Frame hinzugefügt, wenn das Frame erstellt wird.

.. XXX Frames beschreiben?

Was passiert jetzt, wenn man in *inner()* *outer_name* einen Wert
zuweist?

.. code-block:: python

   def outer():
       outer_name = 42
   
       def inner():
           outer_name = 43
   
       return inner

.. code-block:: text

     5           0 LOAD_CONST               1 (43)
                 3 STORE_FAST               0 (outer_name)
                 6 LOAD_CONST               0 (None)
                 9 RETURN_VALUE

Wie man sieht, wird *outer_name* in *inner()* automatisch zu einer
lokalen Variable, der Wert in *outer()* selbst wird nicht
geändert. Versucht man vorher außerdem auf *outer_name* zuzugreifen,
erhält man einen *UnboundLocalError*.


Für diesen Fall bietet Python 3 das neue *nonlocal*\ -Statement. Damit
kann man in *inner()* sagen, dass man den Wert in *outer()* ändern
mag:

.. code-block:: python3

   def outer():
       outer_name = 42
       
       def getter():
           return outer_name
       
       def increaser(n):
           nonlocal outer_name
           outer_name += n
       
       return (getter, increaser)
   
   (getter, increaser) = outer()
   print(getter())
   increaser(42)
   print(getter())

Führt man den Code aus, erhält man die folgende Ausgabe:

.. code-block:: text

   42
   84

Doch wie funktioniert *nonlocal*? Schauen wir uns dazu wieder den
Bytecode an. Von *getter()*:

.. code-block:: text

     5           0 LOAD_DEREF               0 (outer_name)
                 3 RETURN_VALUE

Wenig überraschend hat sich hier nichts geändert. Und der Bytecode von
*increaser()*?

.. code-block:: text

     9           0 LOAD_DEREF               0 (outer_name) 
                 3 LOAD_FAST                0 (n) 
                 6 INPLACE_ADD          
                 7 STORE_DEREF              0 (outer_name) 
                10 LOAD_CONST               0 (None) 
                13 RETURN_VALUE

Wie man sieht, wird zum Laden der Variable wieder ``LOAD_DEREF``
benutzt. Was jetzt aber interessant ist: Zum Speichern wird
``STORE_DEREF`` benutzt, also derselbe Opcode, der auch in *outer()*
benutzt wird. Was ja auch eigentlich logisch ist, denn in beiden
Fällen wird der Wert in ein Cell-Objekt geschrieben -- sogar in
dasselbe Cell-Objekt. Das bringt uns also zur folgenden Erkenntnis:
Das `nonlocal`-Statement wäre auch problemlos in Python 2.x möglich,
es fehlt nur die Syntax dafür (und natürlich auch die
Compiler-Unterstützung).

Also werden wir im Folgenden probieren, das *nonlocal*\ -Statement in
Python 2.x umzusetzen. Dazu müssen in der inneren Funktion alle
``STORE_FAST``\ -Opcodes für einen nonlocal-Namen durch ``STORE_DEREF``
ersetzt werden und alle ``LOAD_FAST`` durch ``LOAD_DEREF``. Außerdem
müssen die Namen dann zu *co_freevars* hinzugefügt werden. Man kann
ein Code-Objekt jedoch nicht einfach so verändern, sondern muss ein
neues erstellen. Da man Funktionen verändert, drängt sich ein
Dekorator geradezu auf:

.. code-block:: python

   def nonlocal(*args):
       def decorator(f):
           code = Code.from_code(f.func_code)
           code.freevars.extend(args)
           for (i, (op, arg)) in enumerate(code.code):
               if op in ["LOAD_FAST", "STORE_FAST"]:
                   name = code.code_obj.co_varnames[arg]
                   if name in args:
                       if op == "LOAD_FAST":
                           code.code[i] = ("LOAD_DEREF", code.freevars.index(name))
                       else:
                           code.code[i] = ("STORE_DEREF", code.freevars.index(name))
   
           caller_locals = sys._getframe(1).f_locals
           return types.FunctionType(
               code.to_code(),
               f.func_globals,
               f.func_name,
               f.func_defaults,
               tuple(caller_locals["_[%s]" % (name, )] for name in args)
           )
       return decorator

Dabei zeigt sich ein weiteres Problem: Man muss an die Cell-Objekte
der äußeren Funktion bekommen. Dies tun wir, indem wir nach jedem
*STORE_DEREF* (also jedes mal, wenn ein Wert in ein Cell-Objekt
geschrieben wird), zwei weitere Opcodes einfügen: ``LOAD_CLOSURE`` und
``STORE_FAST``. Damit wird direkt nach dem Speichern das Cell-Objekt auf
den Stack geladen und in einem lokalen Namen gespeichert. Dazu führen
wir für jeden Namen, der ein Cell-Objekt hat, eine lokale Variable
*_[<Name>]* ein. Die *[]* deshalb, dass der Name nicht mit einem
anderen lokalen Namen zu Konflikten führt. Im Dekorator der inneren
Funktion kann man dann einfach über ``f_locals`` vom Frame des
Aufrufers auf die Cell-Objekte zugreifen, den man mit
``sys_getframe(1)`` bekommt. Der Dekorator für die äußere Funktion
sieht also so aus:

.. code-block:: python

   def outer(*args):
       def decorator(f):
           code = Code.from_code(f.func_code)
           code.varnames.extend("_[%s]" % (name, ) for name in args)
           code.nlocals += len(args)
           code.cellvars.extend(args)
   
           i = 0
           while i < len(code.code):
               (op, arg) = code.code[i]
               if op == "STORE_DEREF":
                   if arg < len(code.cellvars) and code.cellvars[arg] in args:
                       name = code.cellvars[arg]
                       code.code[i+1:i+1] = [
                           ("LOAD_CLOSURE", arg),
                           ("STORE_FAST", code.varnames.index("_[%s]" % (name, )))
                       ]
                       i += 2
               i += 1
                           
           f.func_code = code.to_code()
           return f
       return decorator

Und die Dekoratoren können dann wie folgt benutzt werden:

.. code-block:: python

   import nonlocal
   
   @nonlocal.outer("a")
   def spam():
       a = 23
   
       def getter():
           return a
   
       @nonlocal.nonlocal("a")
       def increaser(n):
           a += n
   
       return (getter, increaser)
   
   g, i = spam()
   assert g() == 23
   i(19)
   assert g() == 42

Dabei ist anzumerken, dass dabei nicht alle Fälle abgedeckt sind und
außerdem davon ausgegangen wird, dass die äußere Funktion bereits
Cell-Objekte für die nonlocal-Namen benutzt (in diesem Fall wird dies
ausgelöst durch die *getter()*\ -Funktion).

Außerdem wird *Code*\ -Klasse von Aaron Gallagher benutzt, die bereits
aus einem vorigen `Blogeintrag bekannt ist <|filename|tco.rst>`_:

.. code-block:: python

   class Code(object):
       @classmethod
       def from_code(cls, code_obj):
           self = cls()
           self.code_obj = code_obj
           self.cellvars = list(code_obj.co_cellvars)
           self.freevars = list(code_obj.co_freevars)
           self.names = list(code_obj.co_names)
           self.nlocals = code_obj.co_nlocals
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
       
           return types.CodeType(code_obj.co_argcount, self.nlocals, 
               code_obj.co_stacksize, code_obj.co_flags, co_code.tostring(), 
               tuple(self.consts), tuple(self.names), tuple(self.varnames), 
               code_obj.co_filename, code_obj.co_name, code_obj.co_firstlineno,
               co_lnotab.tostring(), tuple(self.freevars), tuple(self.cellvars))
