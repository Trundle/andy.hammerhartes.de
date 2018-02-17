=============================================
Finding bugs in systems through formalization
=============================================

:date: 2018-02-10 21:48
:tags: en, tlaplus, pluscal
:status: draft


Introduction
============

Welcome to the first post in English! Today’s post is about how creating a
formal specification for (parts of) a system can help finding real-world bugs.
What initially triggered this post was that I watched `Hillel Wayne's Strange
Loop talk "Tackling Concurrency Bugs with TLAplus"
<https://www.youtube.com/watch?v=_9B__0S21y8>`_. Having dealt with a concurrency
bug at work the week before, I thought it would be the perfect opportunity to
learn some TLA+ and to verify the existence of the bug with TLA+. That turned
out to work so well that it was worth writing a blog post about it, hence here
we are!


Overview of the problem at hand
===============================

The system that this post about is a system that processes some kind of jobs.
Processing one job consists of multiple different steps, possibly being done in
parallel. Each processing steps publishes status updates. A supervisor, called
*processing handler*, supervises the processing. Once the processing of all
mandatory steps has finished, some additional action is triggered, for example
updating some metric or inform other parts of the system about the completed
processing.

While not all mandatory steps are completed, the job is said to be in a
*pending* state. Once all the mandatory steps are complete, the job is in the
*completed* state.

.. image:: |filename|/images/formalizing-the-system.png

.. @startuml

   queue "Message Queue" as rabbitmq
   
   rectangle "Some Processing Step" as step1
   rectangle "Another Processing Step" as step2
   
   step1 --> rabbitmq: Sends completed status message
   step2 --> rabbitmq
   
   rectangle "Progress Handler" as handler {
     rectangle "Instance 1" as handler1
     rectangle "Instance 2" as handler2
   }
   
   note left of handler
     Collects the status messages and
     decides whether a job is complete
   end note
   
   rabbitmq --> handler: Status messages
   handler1 -- Cassandra
   handler2 -- Cassandra
   
   database Cassandra {
     storage "Node 1" as node1
     storage "Node 2" as node2
     storage "Node 3" as node3
   
     node1 .. node2
     node1 .. node3
     node2 .. node3
   }
   
   @enduml


The issue is now that sometimes, the switch from processing to completed cannot
be observed from within the progress handler.


The progress handler
====================

First, let's have a closer look on the progress handler. It consists of the
following steps:

* Load the job from the database
* Append the new status to the set of statuses
* Load the job again from the database
* Check if the new set is considered “processing is complete”. If that is in
  contrast to the previous set, emit a “processing is now complete” message.

How do we now find out if the design of the progress handler is sound? One
possibility would be to think hard about it. Another possibility is to create a
formal specification and then check the soundness through a model checker. This
post will outline how one can do exactly that with the help of `TLA+
<http://lamport.azurewebsites.net/tla/tla.html>`_. Reasoning about concurrent
systems is hard, but very easy to get wrong. With TLA+, we can make use of
computers for what they are pretty good at: trying out a lot of different steps,
fast, and without errors.

For some more motivation why using TLA+ is a good idea, see `Murat Demirbas's
blog post "Why you should use modeling"
<http://muratbuffalo.blogspot.de/2018/01/why-you-should-use-modeling-with.html>`_.


A bit on TLA+
=============

TLA+ is a formal specification language that can be used to design, model,
document, and verify concurrent systems. The theoretical backgrounds of TLA+ are
`set theory <https://en.wikipedia.org/wiki/Set_theory>`_ and `temporal logic
<https://en.wikipedia.org/wiki/Temporal_logic>`_.

This post hopefully gives enough background on TLA+ enough so readers without
prior knowledge are able to understand the specification outlined in the post.
Following are some additional resources for inclined readers who want to learn a
bit more about TLA+:

* `learntla.com <http://learntla.com>`_
* `Leslie Lamport’s video course <http://lamport.azurewebsites.net/video/videos.html>`_
* `"Resources for Learning About TLA" on the TLA+ site
  <http://lamport.azurewebsites.net/tla/tla.html>`_

Additionally, the presented specification will not be written in TLA+ directly
but in PlusCal. PlusCal is a pseudocode-like language that translates to TLA+.
It is probably a bit easier to read and write for programmers without a strong
background in formal logic.

.. note::

   The term TLA+ will be used rather sloppy in this post. When it’s mentioned
   that *“TLA+ does/check/…”*, it might well be that it’s actually the model
   checker (TLC) which does it or that it’s a property of PlusCal.


Modelling the different parts of the system
===========================================

The queue
---------

The queue we want to model is a FIFO. Like every queue, it supports two
operations: put for adding an element and take to pop an element from the queue.
To keep the specification as simple as possible, we simply begin the model
checking with all status messages that we want to have processed already
enqueued. That leaves us with only needing to model the take operation.

.. code::

   EXTENDS Sequences, TLC
   
   \* Receive a message from the queue
   macro recv(queue, receiver)
   begin
     await queue # <<>>;
     receiver := Head(queue);
     queue := Tail(queue);
   end macro

Hopefully, this doesn’t look too surprising. On the other hand, it’s the first
PlusCal code in this post, hence it’s probably worth looking at it a bit closer
in detail:

* Line comments begin with ``\*``
* It defines the macro recv which takes two arguments. A macro will be expanded
  at the call site at compile time.
* ``#`` means unequal (alternatively, ``/=`` can be used as well)
* ``<<>>`` is an empty tuple
* The macro consists of three different parts:

  * wait until the queue passed as argument is not empty
  * take the head
  * set the queue to the tail elements

Let’s see if this works! We define our queue queue with two messages, another
variable msg where we will store the received messages, add a bit of required
boilerplate and then receive the two messages:

.. code::

   EXTENDS Sequences, TLC
   
   (* --algorithm queue
   variable queue = <<"first message", "second message">>,
     msg = "";
   
   \* Receive a message from the queue
   macro recv(queue, receiver)
   begin
     await queue # <<>>;
     receiver := Head(queue);
     queue := Tail(queue);
   end macro
   
   begin
     recv(queue, msg);
     print msg;
     recv(queue, msg);
     print msg;
   
   end algorithm *)

``print`` is of course a debug utility and nothing that would have a place in a
real specification. If we now translate this PlusCal to TLA+ and execute it, the
output will be ``first message`` and then ``second message``. How you are
actually able to execute this specification is out of scope for this post, but
fortunately Leslie Lamport explains it in his video course, in the video
`"Resources and Tools" <http://lamport.azurewebsites.net/video/video3.html>`_.
`The specification can be found on Github
<https://github.com/Trundle/PlusCal/blob/master/progress/first_queue.tla>`_, in
case you want to toy around with it.

The real progress handler, the one we want to model, is of course more complex.
First of all, it not only receives one message, it rather never stops to receive
messages. There can also be more than one instance of it. Of course PlusCal also
provides a way to model this, in the form of loops and processes.

.. code::

   process handler \in 1..2
   variable msg = "";
   begin 
   loop:
     while TRUE do
       recv(queue, msg);
     end while
   end process

Note that the ``loop:`` is not part of the ``begin`` but defines a label.
Basically everything in one label happens at once and only between labels the
model and its invariants will be checked. Process switches also happen between
labels. TLA+ will choose an arbitrary process and execute one step, again and
again, indefinitely.

If we now run this model, TLA+ will eventually produce an error: *Deadlock
reached*. That is because TLA+ also checks for deadlocks, and eventually all our
processes will wait for a new message to appear in the queue.

Cassandra
---------

Now that we have successfully modelled the queue, let’s move on to Cassandra.
Cassandra is used to persist the set of completed processing steps. In
Cassandra, it's possible to specify a *replication factor* that tells Cassandra
on how many nodes data should be replicated. If one writes data to only one
node, Cassandra will replicate the data in the background to the number of other
nodes specified in the replication factor. It means though that it's possible to
not always read the latest data, for example in the case data is written to one
node and then immediately read from another node and the data is not replicated
yet. Cassandra also offers a *consistency level* for every query, where one can
specify on how many nodes data needs to be written before a write query
completes as successful (or, in the case of read query, from how many different
nodes data needs to be read).

In the blog post's model, the background replication (in other words, the
*replication factor*) is omitted and the consistency level is modelled by taking
a set of nodes for the write operation.

.. code::

   procedure appendProgress(writeNodes, status)
   variable nodes = writeNodes;
   begin P0:
     while (nodes # {}) do
     P1:
       with n \in nodes do
         progress[n] := progress[n] \union {status};
         nodes := nodes \ {n};
       end with
     end while;
     return;
   end procedure

A procedure is similar to a macro, but it can can have labels, so a process
switch in the middle of the execution of the procedure is possible, and it can
have a return value. The ``with n \in nodes`` statement is executed by choosing
any element out of nodes and then executing the statement’s body. This will be
done for every possible execution of the statement, so for every possible
element. That means that ultimately this procedure makes TLA+ check every
possible combination of the order in which the progress is written to the
individual nodes.

Modelling the read could be done in a similar fashion. In this specification,
it’s simplified to the following:

.. code::

   \* Reads the progress set from the given nodes
   ReadProgress(nodes) == UNION {progress[n] : n \in nodes}

What can be seen here is one of the pitfalls of extracting a system’s behaviour
into a specification. The modelling of how Cassandra behaves is of course based
on the the author’s understanding of how Cassandra behaves. If Cassandra behaves
differently for whatever reason (maybe because the author’s understanding was
plain wrong, or maybe because Cassandra might have a bug itself), then the
specification will not reflect how the real system behaves. In this instance,
it’s assumed that when reading a set and different nodes return different sets,
Cassandra will merge the sets of all nodes into one resulting set.

The final progress handler
--------------------------

With having modelled the queue and Cassandra, that leaves the final missing
part: the progress handler itself. As mentioned before, it executes the
following steps:

* Wait for a status queue message. That also increases the number of
  unacknowledged queue messages.
* Load the job from the database
* Append the new status and write it to the database
* Load the job again and check if its overall status switched from *processing*
  to *completed*
* Acknowledge the queue message (mark it as processed).

For consistency reasons, we instruct Cassandra to always read and write from a
majority number of nodes before an operation is considered complete. We also
consider the possibility that the read and write operations use a different set
of nodes. To do so, another helper is introduced to give all subsets of nodes of
a given size:

.. code::

   \* Returs a set with all subsets of nodes with the given cardinality
   NNodes(n) == {x \in SUBSET Nodes : Cardinality(x) = n} 

That helper can then be used to describe the variables in the process that
describes the process handler:

.. code::

   \* Handles a progress message from the queue
   fair process progressHandler \in {"handler1", "handler2"}
   variable
     writeQuorumNodes \in NNodes(Quorum),
     readQuorumNodes \in NNodes(Quorum),
     secondReadQuorumNodes \in NNodes(Quorum),
     completedBefore = FALSE,
     message = "";

Once again, TLA+ will check every possible combination of read and write nodes.

The remaining part of the progress handler is pretty straight forward:

.. code::

   begin P0:
     while TRUE do
     Poll:
       recv(queue, message);
       unacked := unacked + 1;
     Read: 
       completedBefore := ProcessingComplete(ReadProgress(readQuorumNodes)); 
     Write:
       call appendProgress(writeQuorumNodes, message);
     ReadAfterWrite:
       if ~completedBefore /\ ProcessingComplete(ReadProgress(secondReadQuorumNodes)) then
         \* The real progress handler would trigger some action here
         switchHappened := switchHappened + 1;
       end if;
     Ack:
       unacked := unacked - 1;
     end while;
   end process;

As a final step, an invariance called *Correctness* is added to the
specification. TLA+ will check that the invariant holds after every step. One
invariant that should hold at every time for the progress handler is that there
are either still some messages to process (in other words, the queue is not
empty), or that the handler is still in the act of processing a message (number
of unacknowledged messages is not zero) or that the progress switch was observed
by a handler:

.. code::

   Correctness == \/ queue # <<>> 
                  \/ unacked > 0 
                  \/ switchHappened > 0

With the complete specification now in place, the model can be checked. And it
completes without error! `The complete specification can be found on Github
<https://github.com/Trundle/PlusCal/blob/master/progress/progress.tla>`_ in case
you want to check yourself.


Liveness
========

The *Correctness* invariant only checks that the specification doesn’t allow an
erroneous step. It doesn’t give any liveness guarantee, that is that the
progress handler ever processes any messages at all. To also verify that, we can
add a *temporal operator* to the specification, such as ``<>[]``. The ``<>[]``
operator means that the predicate that follows it is expected to be true at some
point and then stays true forever. Hence, to verify that our progress handler
actually does what is expected, the following property can be added to the
specification:

.. code::

   Liveness == <>[](switchHappened > 0)

Luckily, if the model is now executed, it still completes without any error.


The bug
=======

The fact that the model execution completes without any error creates a dilemma:
the switch from *processing* to *completed* is always observed, but the starting
point of this post was that sometimes the switch isn’t observed. So either the
specification doesn’t model one of the involved components such as Cassandra
correctly or the implementation of progress handler doesn’t follow the
specification. Which of the two possibilities is it?

By adding a bit of logging to the actual implementation and staring sharply at
the logs, it can be observed that on the second read, the progress handler
doesn’t read back a progress step it has already seen with the first read. That
should not be possible if quorum reads and writes are used, hence a first guess
would be that no quorums are used in the implementation. The specification can
be used to demonstrate that the progress handler requires quorums. If any of the
``NNodes(Quorum)`` in the *progressHandler* process is changed to ``NNodes(1)``,
executing the model will reveal errors.

The implementation uses Java with the `Datastax Cassandra Driver
<https://github.com/datastax/java-driver>`_ and prepared statements. The
statements are created as following:

.. code:: java

   Statement insert = QueryBuilder
       .insertInto(keyspace, columnFamily)
       // Omitted: binding expressions for the values here …
       .setConsistencyLevel(consistencyLevel);

   return session.prepare(insert.toString());

Rather subtle, but for creating the prepared statement, the string
representation of the created ``Statement`` object is used. Unfortunately, the
string representation doesn’t include the ``Statement``’s consistency level
property! Changing the code to:

.. code:: java

   Statement insert = QueryBuilder
       .insertInto(keyspace, columnFamily)
       // Omitted: binding expressions for the values here …

   return session
          .prepare(insert.toString());
          .setConsistencyLevel(consistencyLevel);

makes the model execute without any error.


Proving more properties
=======================

Having a formal model for the system makes it also possible to check some more
properties for it. For example, one might be interested in how many documents
are processed, say for accounting purposes. The obvious place to add it is in
the progress handler, when the switch from *processing* to *completed* was
observed. If the switch is observed, increase a counter, done. We verified that
the switch is guaranteed to be observed (if the document is processed), hence it
should work fine. There is a caveat though: So far we only checked whether the
switch was observed - what we didn't verify was that it is guaranteed that the
switch is only observed once and not twice or more.

.. code::

   NoDupSwitch == switchHappened <= 1 

Unfortunately, executing this specification will result in an error. It's not
guaranteed that the switch is only observed once, hence using it for increasing
a counter for accounting purposes might charge a customer more than once for a
single document.


Closing words
=============

I hope that I could demonstrate that TLA+ is a useful tool worth adding to your
toolbox. One of its downsides, that it doesn't verify real code, is also one of
its upsides: one can verify designs before even writing any code. Give it a try!
