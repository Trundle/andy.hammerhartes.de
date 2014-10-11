Variable Tab-Breite in Python
=============================


:date: 2010-10-06 23:57:52
:tags: de, python, programming, useless facts


In Python 2 kann man dem Tokenizer mittels Kommentaren mitteilen, wie breit ein Tab ist:

.. code-block:: python

   # :ts=4
   if 1:
       if 0:
           print 1
   	print 2 # hard tab here

Führt man den Code aus, wird ``2`` ausgegeben. Entfernt man den Kommentar, wird nichts ausgegeben.
