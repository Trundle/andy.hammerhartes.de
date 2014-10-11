Automatisiert Refleaks in Unittests erkennen
============================================
:tags: de, programming, python, unittest
:date: 2012-11-11 11:59:47

Wenn man händisch CPython-Erweiterungen mit Hilfe der C-API baut (und
nicht etwa Cython_ oder Ähnliches benutzt), läuft man leider sehr
leicht Gefahr, dass man versehentlich Reference Leaks einbaut.

Um das Auffinden von Refleaks zu erleichtern, zählt CPython bei einem
Debug-Build die Summe aller Referenzen:

.. code-block:: pycon

   Python 3.4.0a0 (default:9214f8440c44, Nov 11 2012, 00:15:25) 
   [GCC 4.7.1] on linux
   Type "help", "copyright", "credits" or "license" for more information.
   >>> 
   [60488 refs]
   >>> n = 42
   [60490 refs]

Die Summe der Referenzen ist die Zahl zwischen den ``[]``. In diesem
Beispiel hat sich die Gesamtanzahl der Referenzen um zwei erhöht, weil
die Zahl 42 an zwei Namen gebunden wurde: einmal an ``n`` und einmal
an ``_``, weil Python im interaktiven Modus immer unter ``_`` eine
Referenz auf den letzten Wert hält.

Die Gesamtanzahl der Referenzen kann man in Debug-Builds auch
programmatisch über die Funktion *sys.gettotalrefcount* erhalten. Also
liegt es nahe, dass man versucht, Refleaks automatisch zu finden,
beispielsweise, indem man die Gesamtanzahl der Referenzen vor und nach
einem Testlauf betrachtet.

Die Idee ist hierbei recht einfach: Wird die Test-Suite mit einem
Debug-Python ausgeführt, wird jeder Test fünf mal ausgeführt. Bei den
letzten zwei Durchläufen wird dann die Gesamtzahl der Referenzen vor
und nach dem Test verglichen. Die drei Durchläufe vorher werden nicht
ausgewertet, damit sich die Zahl der Referenzen erst auf einen Wert
einpendeln kann (beispielsweise, wenn Caches im Test eine Rolle
spielen etc.).

Im Folgenden eine simple Umsetzung der Idee für das klassische
``unittest``-Modul:


.. code-block:: python

   hunt_leaks = hasattr(sys, "gettotalrefcount")
   if hunt_leaks:
       import gc
   
   def _is_not_suite(test):
       try:
           iter(test)
       except TypeError:
           return True
       return False
   
   
   def _cleanup():
       sys._clear_type_cache()
       gc.collect()
   
   def _hunt(test):
       def test_wrapper(*args, **kwargs):
           deltas = []
           _cleanup()
           for i in xrange(5):
               before = sys.gettotalrefcount()
               test(*args, **kwargs)
               _cleanup()
               after = sys.gettotalrefcount()
               if i > 2:
                   deltas.append(after - before)
           if any(deltas):
               print("{0!r} leaks: {1}".format(test, deltas))
       return test_wrapper
   
   class TestSuite(unittest.TestSuite):
       def __iter__(self):
           for test in super(TestSuite, self).__iter__():
               if hunt_leaks and _is_not_suite(test):
                   yield _hunt(test)
               else:
                   yield test

Anzumerken ist hierbei, dass bei umfangreichen Testsuites `_cleanup`
noch erweitert werden muss. Beispielsweise muss man die ABC-Registry
aufräumen, Caches (re, struct, urllib, linecache) und warnings müssen
aufgeräumt werden, etc.

Jetzt muss man nur noch ``unittest`` beibringen, dass es die obige
TestSuite benutzen soll. Benutzt man keinen besonderen Test-Runner,
kann man das beispielsweise einfach wie folgt tun:

.. code-block:: python

   def test():
       loader = unittest.TestLoader()
       loader.suiteClass = TestSuite
       unittest.main(testLoader=loader)
   
   if __name__ == "__main__":
       test()

Reference Leaks können natürlich auch mit "reinem" Python-Code
passieren, indem man globalen Zustand verändert. Ein etwas
konstruiertes Beispiel:

.. code-block:: python

   class Observable(object):
       def __init__(self):
           self.observers = []

       def add_observer(self, callable):
           self.observers.append(callable)

       def notify_observers(self, value):
           for observer in self.observers:
               observer(value)

   value = Observable()

   class SpamTest(unittest.TestCase):
       def test_observable(self):
           class Observer(object):
               def __init__(self):
                   self.called = False

               def __call__(self, value):
                   self.called = True

           observer = Observer()
           value.add_observer(observer)
           value.notify_observers(42)
           self.assertTrue(observer.called)

Führt man die Tests jetzt aus, führt das zu folgender Ausgabe::

  .....<__main__.SpamTest testMethod=test_observable> leaks: [40, 40]

  ----------------------------------------------------------------------
  Ran 5 tests in 0.007s

Jetzt weiß man zumindest, dass der Test ``test_observable`` leckt. Was
genau leckt, muss man aber immer noch selbst herausfinden. Was nicht
unbedingt immer leicht und offensichtlich ist.

.. _Cython: http://cython.org/
