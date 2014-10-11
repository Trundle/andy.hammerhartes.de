Ausgabe in der Python-REPL abschneiden
======================================

:date: 2009-09-23 16:48:27
:tags: de, python

Dazu benutzt man einfach *sys.displayhook*. bpython und Python führen
beim Starten die Datei aus, auf die die Umgebungsvariable
``PYTHONSTARTUP`` zeigt. Man kann sich also einfach eine Datei mit
folgendem Inhalt anlegen:

.. code-block:: python
		
   import __builtin__
   import sys
   
   def displayhook(value):
       if value is not None:
           __builtin__._ = value
           out = repr(value)
           if len(out) > 42:
               out = out[:42] + '... (truncated)'
           print out
   sys.displayhook = displayhook

Dann wird die Ausgabe automatisch abgeschnitten. Mag man dann die
eigentliche Ausgabe, kann man ``print _`` bzw. ``print repr(_)``
benutzen.
