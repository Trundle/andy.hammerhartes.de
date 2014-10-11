Wegoptimierte Syntaxfehler
==========================

:date: 2009-08-24 02:55:52
:tags: programming, python, useless facts


Manche Syntaxfehler können in CPython wegoptimiert werden:

.. code-block:: python

   >>> if 0:
   ...     yield
   ... 
   >>> if 1:
   ...     yield
     File "<input>", line 2
   SyntaxError: 'yield' outside function (<input>, line 2)		
