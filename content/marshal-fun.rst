marshal-Spaß
============

:date: 2009-09-30 12:04:51
:tags: de, python, useless facts

.. code-block:: pycon

   >>> import marshal
   >>> marshal.loads('l\x02\x00\x00\x00\x00\x00\x00\x00')
   00000L
   >>> bool(_)
   True
   >>>
