Der "läuft gegen"-Operator in C++
=================================

:tags: de, programming, c++
:date: 2009-12-31 01:00:43


.. code-block:: c++

   #include <iostream>
   
   int main(int argc, char **argv)
   {
       int x = 10;
   
       // x goes to 0
       while (x --> 0)
           std::cout << x << std::endl;
   }
