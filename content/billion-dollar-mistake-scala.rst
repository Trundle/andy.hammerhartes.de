=========================================
The billion dollar mistake, Scala edition
=========================================

:date: 2018-06-03 18:00
:tags: en, scala, paper, programming

Prologue
========

Today's blog post originates from an internal presentation at my workplace and
describes the paper `Java and Scala’s Type Systems are Unsound
<http://io.livecode.ch/learn/namin/unsound>`_ by Amin and Tate. Hence the
presented ideas are not really my own and all the praise goes to the paper's
authors. All mistakes are, of course, mine alone.

By the end of the post, you will see how to provoke a ``ClassCastException`` at
runtime without ever using a cast (or Scala's equivalent of a cast,
``asInstanceOf``). This post shows the Scala version of the paper, but it's worth
to mention that the same can be done for Java's type system (as shown in the
paper).

You can find a Jupyter notebook version of the blogpost `here
<https://gist.github.com/Trundle/3a514e62ccadbd8667>`_. It requires the `Jupyter
Scala kernel <https://github.com/jupyter-scala/jupyter-scala>`_ to run.

Subtyping
=========

If ``S`` is a subtype of ``T``, any term of type ``S`` can be safely
used in a context where a term of type ``T`` is expected. This subtyping
relation is often written as ``S <: T``. The subtyping relation
typically is also reflexive (``A <: A``) and transitive (``A <: B`` and
``B <: C`` implies ``A <: C``), making it a preorder.

Example: ``Integer <: Number <: Object``

Subtyping is also a form of type polymorphism (a single interface to
entities of different types), namely *subtype polymorphism*. Example:
``ArrayList <: List``.

Path-dependent types
====================

Scala has path-dependent types. They allow values to have individualized
types associated with them. Note that the type is associated with the
value, not with the value’s type!

For example, given the following trait:

.. code:: scala

    trait Box {
        type Content
        def revealContent(): Content
    }




.. parsed-literal::

    defined trait Box



and the following two values:

.. code:: scala

    val box1: Box = new Box {
        type Content = Int
        def revealContent(): Int = 42
    }
    
    val box2: Box = new Box {
        type Content = Int
        def revealContent(): Int = 21 + 21
    }
    
    // Note the different types and specifically that it's not Box.Content!
    var content1: box1.Content = box1.revealContent()
    val content2: box2.Content = box2.revealContent()




.. parsed-literal::

    box1: Box = $sess.cmd1Wrapper$Helper$$anon$1@387d316
    box2: Box = $sess.cmd1Wrapper$Helper$$anon$2@6cdc9e37
    content1: box1.Content = 42
    content2: box2.Content = 42



Then all of the following is not possible:

.. code:: scala

    val c: Box.Content = box1.revealContent()


.. parsed-literal::

    cmd2.sc:1: not found: value Box
    val c: Box.Content = box1.revealContent()
           ^

    Compilation Failed


.. code:: scala

    // Note the mix of box1 and box2!
    val c2Prime: box1.Content = box2.revealContent()


.. parsed-literal::

    cmd2.sc:1: type mismatch;
     found   : cmd2Wrapper.this.cmd1.wrapper.box2.Content
     required: cmd2Wrapper.this.cmd1.wrapper.box1.Content
    val c2Prime: box1.Content = box2.revealContent()
                                                  ^

    Compilation Failed


Using (witness) values to reason about code
===========================================

It’s possible to use values as a proof that some other value has a
certain property. For example, we can define a trait ``LowerBound[T]``
that reflects that a value of type ``T`` has a super class ``M``.

.. code:: scala

    // T is a subclass of M
    trait LowerBound[T] {
        type M >: T
    }




.. parsed-literal::

    defined trait LowerBound



Now, with the help of that value, we can write an ``upcast`` function
that casts ``T`` to ``M``, without ever using a cast:

.. code:: scala

    def upcast[T](lb: LowerBound[T], t: T): lb.M = t
    
    // Proof that it works
    val intLowerBound = new LowerBound[Integer] {
        type M = Number
    }
    
    val int42: Integer = 42
    val intAsNumber: Number = upcast(intLowerBound, int42)




.. parsed-literal::

    defined function upcast
    intLowerBound: AnyRef with LowerBound[Integer]{type M = Number} = $sess.cmd3Wrapper$Helper$$anon$1@306ad96a
    int42: Integer = 42
    intAsNumber: Number = 42



Note that it works because we state the subtyping relation ``M >: T``
and Scala verifies that the relation holds. For example, trying to state
that ``Integer`` is a lower bound of ``String`` doesn’t work:

.. code:: scala

    val intWithStringAsLowerBound = new LowerBound[Integer] {
        type M = String
    }


.. parsed-literal::

    cmd4.sc:2: overriding type M in trait LowerBound with bounds >: Integer;
     type M has incompatible type
        type M = String
             ^

    Compilation Failed


Reasoning about nonsense
========================

Now comes the fun part: reasoning about nonsense. First, we introduce a
complementary trait ``UpperBound[U]`` that states that ``U`` is a
subtype of ``M``.

.. code:: scala

    trait UpperBound[U] {
        type M <: U
    }




.. parsed-literal::

    defined trait UpperBound



In Scala, it’s possible for a value to implement multiple, traits, hence
we can have a value of type ``LowerBound[T] with UpperBound[U]`` which
states the subtype relation ``T <: M <: U`` (that’s the reason why we
named the path-dependent type in both traits ``M``, so we can express
this relation).

Note that a type system always only helps so much. We made the type
system argue for us about certain values, but the type system doesn’t
hinder us from expressing complete nonsense. For example, the following
compiles perfectly fine:

.. code:: scala

    // We take a proof `bounded` that states that String <: M <: Integer and a value of
    // bottom type String, and we will raise to the top and return an integer
    def raiseToTheTop(bounded: LowerBound[String] with UpperBound[Integer], value: String): Integer = {
        // Subtle, but: the LowerBound[String] allowes the upcast (because String <: M)
        // On the other hand, the `UpperBound[Integer]` states that M <: Integer holds
        // as well and because Scala allows subtypes as return value, we are totally fine
        // returing the (intermediate) M as Integer!
        return upcast(bounded, value)
    }




.. parsed-literal::

    defined function raiseToTheTop



Of course nothing good can come from such a function. On the other hand,
we can argue that while it’s a bit sad that the type system allows to
express such a type, nothing bad can happen really happen. The function
above only works because we have proof that the typing relation exists,
via the ``bounded`` witness value. We can only call the function if we
get hold of such a witness value. And we have seen above that it’s
impossible to construct such a witness value, because Scala checks the
typing relation expressed in the traits:

.. code:: scala

   val proof = new LowerBound[String] with UpperBound[Integer] {
       type M = ??? // what should we put here?
   }

The billion dollar mistake
==========================

Tony Hoare, the “inventor” of ``null``, once called it his billion
dollar mistake:

   I call it my billion-dollar mistake. It was the invention of the null
   reference in 1965. At that time, I was designing > the first
   comprehensive type system for references in an object oriented
   language (ALGOL W). My goal was to ensure that all use of references
   should be absolutely safe, with checking performed automatically by
   the compiler. But I couldn’t resist the temptation to put in a null
   reference, simply because it was so easy to implement. This has led
   to innumerable errors, vulnerabilities, and system crashes, which
   have probably caused a billion dollars of pain and damage in the last
   forty years.

And, as you might have already guessed from the title, it haunts as
again. Scala has the concept of implicit nulls, meaning that a ``null``
value can take any type. Unfortunately for us, it also means that it can
take the nonsense type ``LowerBound[String] with UpperBound[Integer]``:

.. code:: scala

    val sadness: LowerBound[String] with UpperBound[Integer] = null
    
    // Et voilà, watch the impossible being possible
    raiseToTheTop(sadness, "and that is why we can't have nice things")


::


    java.lang.ClassCastException: java.lang.String cannot be cast to java.lang.Integer

      $sess.cmd5Wrapper$Helper.raiseToTheTop(cmd5.sc:6)

      $sess.cmd6Wrapper$Helper.<init>(cmd6.sc:4)

      $sess.cmd6Wrapper.<init>(cmd6.sc:139)

      $sess.cmd6$.<init>(cmd6.sc:90)

      $sess.cmd6$.<clinit>(cmd6.sc:-1)


A ``ClassCastException`` was thrown - and we didn’t even use a single
cast in our code.

As a matter of fact, we can generalize our ``raiseToTheTop`` function to
coerce an arbitrary type to any type we want:

.. code:: scala

    def coerce[T, U](t: T): U = {
        val bounded: LowerBound[T] with UpperBound[U] = null
        return upcast(bounded, t)
    }
    
    // Same as before
    coerce[String, Integer]("and that is why we can't have nice things")


::


    java.lang.ClassCastException: java.lang.String cannot be cast to java.lang.Integer

      $sess.cmd7Wrapper$Helper.<init>(cmd7.sc:7)

      $sess.cmd7Wrapper.<init>(cmd7.sc:139)

      $sess.cmd7$.<init>(cmd7.sc:90)

      $sess.cmd7$.<clinit>(cmd7.sc:-1)

