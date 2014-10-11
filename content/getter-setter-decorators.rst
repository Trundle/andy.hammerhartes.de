Getter und Setter mit Dekoratoren unter Python 2.6
==================================================


:date: 2009-11-14 11:43:14
:tags: programming, python


.. code-block:: python

   class Spam(object):
       def __init__(self, value):
           self.value = value
   
       @property
       def spam(self):
           return self.value
   
       @spam.setter
       def spam(self, value):
           self.value = value
   
   spam = Spam(42)
   print spam.spam
   spam.spam = 23
   print spam.spam
