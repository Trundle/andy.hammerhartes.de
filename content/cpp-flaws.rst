Every language has its flaws - C++
==================================

:date: 2010-03-06 13:45:15
:tags: programming, c++


Scott Meyers auf die Frage, welche drei Dinge er am wenigsten mag in C++:

  I'd like to answer this question with "complexity, complexity,
  complexity!", but naming the same thing three times is
  cheating. Still, I think that C++'s greatest weakness is
  complexity. For almost every rule in C++, there are exceptions, and
  often there are exceptions to the exceptions. For example, const
  objects can't be modified, unless you cast away their constness, in
  which case they can, unless they were originally defined to be
  const, in which case the attempted modifications yield undefined
  behavior.

Das gesamte (zugegebenermaßen schon etwas ältere) Interview gibt es `hier <http://web.archive.org/web/20080521011500/http://www.bookpool.com/ct/98031>`_.
