==============================================================
Regex improvements in OpenJDK 9: Less exponential backtracking
==============================================================

:date: 2018-05-15 23:15
:tags: en, java, openjdk

I'm trying to keep the current blog post run going (at least compared to the
last years) by blogging about random things I observe or learn. Today's post: I
found out by coincidence that OpenJDK 9 changed a detail about how regular
expressions are matched. The post is not about regular expressions in general,
but regular expressions as implemented by OpenJDK's ``java.util.regex.Pattern``.


Exponential backtracking
========================

The post's title already spoils it: the change is related to backtracking.
OpenJDK's ``Pattern`` implements quantifiers in regular expressions by trying
out the different possibilities and it then backtracks in case there was no
match. So for example, to see if ``a`` matches the pattern ``a?a``, first the
pattern ``aa`` is tried and because it doesn't match (not enough *a*\ s in the
input), the matching backtracks to the beginning and tries the pattern ``a``
next, which then succeeds.

Now let's see what happens if the input ``1111a`` is matched against the pattern
``(1*)*`` in OpenJDK 8, like in the following code:
``Pattern.compile("(1*)*").matcher("1111a").matches()``). In words: in a group,
match zero or more *1*\ s and repeat that group zero or more times.

In the beginning, the ``1*`` inside the group matches greedily all characters
*1* in the input until the *a*. Then the remaining input (the *a*) is used as
input for the remaining part of the regex, which is the group repetition. The
group is repeated again, but ``1*`` still doesn't match the *a* and the matching
fails because not all input is used. Note that the implementation is smart
enough to not try to repeat the group forever with a zero-width match for
``1*``.

The implementation then remembers that in the beginning, it consumed all the
*1*\ s greedily. The question is: would the regex probably match the input if
the first greedy matching doesn't consume all the *1*\ s, but all except the
last one? So the implementation backtracks to the point where it consumed all
but the last *1* and then tries to match the remaining regex against the input
``1a``. This approach still doesn't result in a match. That means another
backtrack and ``11a`` is tried next. The big problem is now: that input ``11a``
will be again first matched greedily by ``1*``, because *remaining regex* means
the group repetition. And as there is still no match due to the trailing *a*,
this matching as part of the backtracking will backtrack as well.

In other words, for every character ``1`` in the input, there are two choices:
match and consume the character as part of the sub-expression ``1*`` or don't
match and continue with the remaining expression (the group repetition). That
results in :math:`2^n` different combinations that need to be tested, with
:math:`n` being the number of leading *1*\ s in the input. There will never be a
match, but that will only be known after every combination has been tested. So,
exponential runtime.

This is not exactly big news. The phenomena of catastrophic backtracking is well
understood and there are various ways how either the regular expression can be
changed to avoid the backtracking (see for example `The Explosive Quantifier
Trap <The Explosive Quantifier Trap>`_ ) or how regexes can be implemented
without backtracking (see for example `Regular Expression Matching Can Be Simple
And Fast`_). It is even known as an attack under the name *ReDoS* and `has its
own OWASP entry
<https://www.owasp.org/index.php/Regular_expression_Denial_of_Service_-_ReDoS>`_.


The change in OpenJDK 9
=======================

In OpenJDK, `an optimization was added
<http://hg.openjdk.java.net/jdk9/client/jdk/rev/d0c319c32334>`_ to avoid the
exponential backtracking. Whenever a greedy repetition (``*``, ``+``, curly
braces, etc) doesn't match some input, the input's cursor position is memoized.
Then, when the repetition is executed again during backtracking, it's checked
whether it already failed to match for this cursor position and if so, the
repetition isn't tested at all (as it will fail no match).

How does that help against exponential backtracking? Let's have a look again at
the previous regex ``(\d*)`` that should match the input ``1111a``. First the
greedy match of the *1*\ s, then the failed attempt to match *a* and then the
backtracking of the first greedy match. The first backtracking attempt is with
the remaining input ``1a``. It doesn't match and it's memoized that this input
failed. Then ``11a`` is tried next. It also fails to match, but it also
backtracks itself due to the first greedy match on the leading ``11``. During
that backtracking, the inputs ``1a`` and ``11a`` need to be tested, but only the
former is actually tested, due to the latter being memoized to have failed.
Hence the backtracking is now linear instead of exponential.

Note that this optimization only works if the pattern doesn't use any
backreferences.

More questions? Then study `the source
<http://hg.openjdk.java.net/jdk9/client/jdk/file/65464a307408/src/java.base/share/classes/java/util/regex/Pattern.java>`_
of OpenJDK's ``Pattern`` implementation!


.. _Regular Expression Matching Can be Simple And Fast: https://swtch.com/%7Ersc/regexp/regexp1.html
