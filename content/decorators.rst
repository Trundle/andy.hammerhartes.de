Dekoratoren in Python, erklärt in Farbe
=======================================

:date: 2014-08-20 22:37:39
:tags: de, python, dekoratoren


Präambel
--------

Dieser Artikel ist schon ein paar Jahre alt und war eigentlich nur für
den Gebrauch bei meinem damaligen Arbeitgeber gedacht. Damit sich aber
endlich mal etwas in diesem Blog tut, habe ich mich entschlossen, ihn
dennoch zu veröffentlichen.

.. note:: Die Code-Beispiele sind in Python 2-Syntax gehalten. Das
          Übersetzen nach Python 3 wird dem Leser als Übung
          überlassen.


Was sind Dekoratoren?
---------------------

Wie der Namen bereits vermuten lässt, dekorieren Dekoratoren
etwas. Bei Python sind es Funktionen bzw. Methoden und seit Version
2.6/3.0 auch Klassen. Ein Beispiel für Dekoratoren:

.. code:: python

   @decorator
   def spam():
       print "Ich bin spam."

.. note:: Ein Hinweis für Java-Entwickler: Die Syntax sieht zwar
          ähnlich aus wie Annotations in Java, hat aber ansonsten
          nichts mit Annotations in Java zu tun.


Was passiert jetzt, wenn man den obigen Code ausführt?


.. code:: pycon

   >>> @decorator
   ... def spam():
   ...     print "Ich bin spam."
   ... 
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
   NameError: name 'decorator' is not defined

Der ``NameError`` ist jetzt natürlich wenig überraschend, schließlich
wurde der Dekorator ``decorator`` noch nicht definiert. Im Folgenden
werden wir das nachholen:


.. code:: python

   def decorator(func):
       print "Ich bin ein Dekorator und dekoriere", func.__name__
       return func

Was passiert jetzt, wenn man den obigen Code ausführt?

.. code:: python

   >>> def decorator(func):
   ...     print "Ich bin ein Dekorator und dekoriere", func.__name__
   ...     return func
   ... 
   >>> @decorator
   ... def spam():
   ...     print "Ich bin spam."
   ... 
   Ich bin ein Dekorator und dekoriere spam
   >>> spam
   <function spam at 0x7f8d95b3c488>

Und was, wenn man die dekorierte Funktion ausführt?

.. code:: python

   >>> spam()
   Ich bin spam.

Wie einfach zu erkennen ist, hat unser simpler Beispiel-Dekorator
keine direkte Auswirkung auf die dekorierte Funktion.



Ich weiß jetzt noch immer nicht, was ein Dekorator ist
------------------------------------------------------

Ein Beispiel alleine erklärt natürlich nicht, was ein Dekorator
ist. Was ist also ein Dekorator? Ein Dekorator ist nichts anderes als
ein Callable, das implizit als Argument die zu dekorierende Funktion
bzw. Methode bzw. Klasse übergeben bekommt. Der Rückgabewert des
Dekorators wird dann an den Namen der Funktion bzw. Methode
bzw. Klasse gebunden. Anders ausgedrückt:

.. code:: python

   @decorator
   def spam():
       pass

ist nichts anderes als syntaktischer Zucker für

.. code:: python

   def spam():
       pass
   spam = decorator(spam)

Das ist auch der Grund, warum unser Beispieldekorator ``decorator``
die Funktion explizit wieder zurück gibt.

Das, was nach dem ``@`` folgt, muss jedoch nicht zwingend ein Name
sein. Vielmehr kann es ein beliebiger Ausdruck sein. Der Ausdruck
wird evaluiert und das Ergebnis des Ausdrucks ist dann der Dekorator.
Um das zu verdeutlichen, folgt jetzt ein Beispiel für eine
Dekoratoren-Factory:

.. code:: python

   def decorator_for(name):
       """Ich bin eine Factory und ich gebe einen Dekorator zurück."""
       print "Erzeuge einen Dekorator für", name
       # Den eigentlichen Dekorator (aus dem vorigen Beispiel) zurück geben
       return decorator

   @decorator_for("Csaba")
   def spam():
       print "Ich bin spam."

Und wieder die Frage, was passiert, wenn man den Code ausführt?

.. code:: pycon
   
   >>> def decorator_for(name):
   ...     """Ich bin eine Factory und ich gebe einen Dekorator zurück."""
   ...     print "Erzeuge einen Dekorator für", name
   ...     # Den eigentlichen Dekorator (aus dem vorigen Beispiel) zurück geben
   ...     return decorator
   ... 
   >>> @decorator_for("Csaba")
   ... def spam():
   ...     print "Ich bin spam."
   ... 
   Erzeuge einen Dekorator für Csaba
   Ich bin ein Dekorator und dekoriere spam

Und was passiert, wenn man die dekorierte Funktion ausführt?

.. code:: pycon

   >>> spam()
   Ich bin spam.

Wie zu erwarten, noch immer nichts spektakuläres.



Wann wird ein Dekorator ausgeführt?
-----------------------------------

Der aufmerksame Leser kann sich diese Frage bereits selbst
beantworten: Der Dekorator wird nicht etwa bei jedem Aufruf der
dekorierten Funktion bzw. Methode aufgerufen, sondern genau ein
einziges Mal, nämlich dann, wenn die Funktion bzw. Methode deklariert
wird.


Ich will aber, dass bei jedem Funktionsaufruf etwas passiert
------------------------------------------------------------

Auch das kann sich der aufmerksame Leser bereits selber herleiten: Wie
bereits erwähnt, wird der Rückgabewert des Dekorators an den Namen der
Funktion gebunden, die dekoriert wird. Als Beispiel also jetzt ein
Dekorator, der *nicht* explizit die dekorierte Funktion wieder
zurückgibt.

.. code:: python

   def useless_decorator(func):
       return None

.. code:: pycon

   >>> @useless_decorator
   ... def spam():
   ...     print "Ich bin spam."
   ... 
   >>> spam()
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
   TypeError: 'NoneType' object is not callable
   >>> spam
   >>>

Da der Dekorator ``None`` zurückgibt, wird auch ``None`` an den Namen
der Funktion, also ``spam``, gebunden und die ursprüngliche Funktion
ging verloren.

Man kann jetzt natürlich nicht nur die Original-Funktion oder ``None``
zurück geben. Vielmehr kann man auch einen Wrapper zurück geben, der
dann die ursprüngliche Funktion aufruft. Damit hat man dann das
erreicht, was man wollte: Bei Jedem Funktionsaufruf soll etwas
passieren.

.. code:: python

   def verbose_caller(func):
       print "Erzeuge einen Wrapper für die Funktion", func.__name__
       
       def wrapper():
           print "Rufe die Funktion", func.__name__, "auf"
   	   func()
       return wrapper

.. code:: pycon

   >>> @verbose_caller
   ... def spam():
   ...     print "Ich bin spam"
   ... 
   Erzeuge einen Wrapper für die Funktion spam
   >>> spam()
   Rufe die Funktion spam auf
   Ich bin spam
   >>> spam
   <function wrapper at 0x7f8d95b3c758>

So gesehen ist der Dekorator in diesem Fall nichts anderes als eine
Wrapper-Factory.

Da das immer noch ziemlich langweilig ist, wollen wir uns jetzt einen
personalisierten Wrapper erzeugen. Dazu bauen wir eine
Wrapper-Factory-Factory:

.. code:: python

   def verbose_caller_for(name):
      print "Erzeuge eine Wrapper-Factory für", name
   
      def verbose_caller(func):
          print "Erzeuge einen Wrapper für die Funktion", func.__name__
   
          def wrapper():
              print "Rufe die Funktion", func.__name__, "für", name, "auf"
              func()
          return wrapper
      return verbose_caller

.. code:: pycon
   
   >>> @verbose_caller_for("Csaba")
   ... def spam():
   ...     print "Ich bin spam"
   ... 
   Erzeuge eine Wrapper-Factory für Csaba
   Erzeuge einen Wrapper für die Funktion spam
   >>> spam()
   Rufe die Funktion spam für Csaba auf
   Ich bin spam

Da das ganze langsam doch recht unübersichtlich wird, überlegen wir
uns als gute Entwickler, wie man das ganze verschönern könnte.


Klassenbasierte Dekoratoren
---------------------------

Dekoratoren sind einfach Callables, die das zu dekorierende Objekt
entgegen nehmen. Instanzen von Klassen können jedoch ein Callable
implementieren, über die spezielle Methode ``__call__``. Warum also
nicht einen Dekorator über eine Klasse implementieren? Als
passionierte Java-Entwickler wissen wir, dass Klassen alles
übersichtlicher machen.

.. code:: python

   class PersonalizedVerboseCaller(object):
       def __init__(self, name):
           self.name = name
   
       def __call__(self, func):
           return self.decorate(func)
   
       def decorate(self, func):
           """Wrapper factory."""
	   print "Erzeuge einen Wrapper für die Funktion", func.__name__
   	   def wrapper():
   	       print "Rufe die Funktion", func.__name__, "für", self.name, "auf"
   	       func()
   	   return wrapper

.. code:: pycon

   >>> @PersonalizedVerboseCaller("Csaba")
   ... def spam():
   ...     print "Ich bin spam"
   ... 
   Erzeuge einen Wrapper für die Funktion spam
   >>> spam()
   Rufe die Funktion spam für Csaba auf
   Ich bin spam
