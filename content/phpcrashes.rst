1001 Wege, PHP zum Segfaulten zu bringen
========================================

:tags: de, programming, php
:date: 2011-09-21 23:25:56

       
Da es aber in etwa so ist wie behinderte Kinder zu schubsen, werde ich nur zwei zeigen.


.. code-block:: php

   <?PHP

   class Spam {
       function __toString() {
           (string)$this;
       }
   };

   (string)new Spam();

   ?>


.. code-block:: php

   <?PHP

   $spam = array();
   implode(&$spam, &$spam);

   ?>
