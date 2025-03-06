.. _api:

API
===

.. testsetup:: *

   from liblet import Production, Item, closure, show_calls, Transition

Symbols, alphabets, words, and languages
----------------------------------------

This library main focus are *formal languages*, with particular attention to
*parsing* aspects.

It is hence important first of all to focus on how **symbols** are represented;
to keep things simple (and make the library more interoperable with the rest of
Python data structures), in LibLet there isn't a specific *type* for such
entities that are always represented by :obj:`strings <str>` (possibly longer
that one character). Observe in passing that Python hasn't a type for
*characters*, but uses strings of length one to represent them.

It is straightforward then to conclude that **alphabets** are represented by
:obj:`sets <set>` of strings.

On the other hand, one must pay particular attention to **words** that are
represented as *sequences* of strings, most commonly :obj:`tuples <tuple>` or
:obj:`lists <list>`. It will never be the case that a LibLet *word* coincides
with a Python *string*! In the very particular case in which all the symbols
have length one (as Python strings) one can use the shortcuts ``list(s)`` and
``''.join(w)`` to go from string to words, and vice versa.

Finally, **languages** are represented by :obj:`sets <set>` of sequences of
strings.


Productions, Grammars, and Derivations
--------------------------------------

.. currentmodule:: liblet.grammar

The basic building block of a *grammar* is a *production* represented by the following class.

.. autoclass:: Production

   In order to find productions satisfying a set of properties, a convenience method
   to build a predicate from a set of keyword arguments is provided.

   .. testsetup:: *

      from liblet import Productions

   .. automethod:: such_that

.. autoclass:: Productions

   A convenience method is provided to obtain productions from a suitable string
   representation of them.

   .. automethod:: from_string

For the purpose of presenting the `Knuth Automaton <https://en.wikipedia.org/wiki/LR_parser#Finite_state_machine>`__
in the context of LR(0) parsing,  productions are extended to include a dot in the following class.

.. autoclass:: Item

   The class has just two metods, useful for the construction of the Knuth Automaton.

   .. automethod:: advance

   .. automethod:: symbol_after_dot

A grammar can be represented by the following class, that can be instantiated
given the usual formal definition of a grammar as a tuple.

.. autoclass:: Grammar

   Even in the case of grammars, a convenience method is provided to build a
   grammar from a suitable string representation. Once the productions are obtained
   with :func:`Productions.from_string`, the remaining parameters are
   conventionally inferred as detailed below.

   .. automethod:: from_string

   An utility method is provided to enumerate alternatives for a given left-hand side:

   .. automethod:: alternatives

   To implement grammar "cleanup strategies" a method to eliminate unwanted symbols (and productions)
   from a grammar is also provided.

   .. automethod:: restrict_to

Once a grammar has been defined, one can build derivations with the help of the
following class.

.. autoclass:: Derivation

   .. automethod:: step

   .. automethod:: leftmost

   .. automethod:: rightmost

   .. automethod:: possible_steps

   .. automethod:: steps

   .. automethod:: sentential_form

Derivations can be displayed using a :class:`~liblet.display.ProductionGraph`.

Transitions and Automata
------------------------

.. currentmodule:: liblet.automaton

Albeit in the context of parsing (that is the main focus of this library), the
role of *finite state automata* and *regular grammars* is not the main focus, a
couple of classes to handle them is provided.

First of all, a basic implementation of a *transition* is provided; as in the
case of grammars, the symbols and terminals are simply :obj:`strings <str>`.

.. autoclass:: Transition

   A convenience method is provided to obtain transitions from a suitable string
   representation of them.

   .. automethod:: from_string


From transitions one can obtain a representation of a (*nondeterministic*)
*finite state automata* using the following class.

.. autoclass:: Automaton

   Even for the automata there are a couple of convenience methods to obtain
   automata from a string representation of the transitions, or from a *regular
   grammar*.

   .. automethod:: from_string

   .. automethod:: from_grammar

    An utility method is provided to represent the *transition function* of the automata.

   .. automethod:: δ

Automata can be displayed using :class:`StateTransitionGraph.from_automaton <liblet.display.StateTransitionGraph.from_automaton>`.

Instantaneous Descriptions
--------------------------

.. currentmodule:: liblet.automaton

During the analysis of some parsing algorithms can be convenient to keep track
of the computation of the related (*nondeterministic*) *pushdown automata*. The
following classes have the purpose to represent an *instantaneous description*
of the automaton given by its stack and, the tape content and the position of
the reading head.

.. autoclass:: InstantaneousDescription

   This is the superclass describing an instantaneous description of an automata; it
   comprises a *tape* and the *head_pos*, a *stack* and a sequence of *steps* that
   have taken the automaton to the current configuration. It is immutable, subclasses
   define how to obtain a new description given a move (that in general differ for
   *top-down* and *bottom-up* parsers).

   .. automethod:: head

   .. automethod:: top

.. autoclass:: TopDownInstantaneousDescription

   This class represents an instantaneous description of an automata performing
   *top-down* parsing; elements on the stack are symbols from the grammar, an
   extra `♯` is added at the bottom of the stack and the end of the tape to
   make it easier to determine if the input word has been accepted.

    .. automethod:: match

    .. automethod:: predict

.. autoclass:: BottomUpInstantaneousDescription

   This class represents an instantaneous description of an automata performing
   *bottom-down* parsing; elements on the stack are the :class:`trees <liblet.display.Tree>` of the parsing forest.

    .. automethod:: shift

    .. automethod:: reduce

ANTLR support
-------------

This module provides a commodity class to deal with `ANTLR <https://www.antlr.org/>`_ for the Python 3 *target*.

.. currentmodule:: liblet.antlr

.. autoclass:: ANTLR

   .. automethod:: load
   .. automethod:: save
   .. automethod:: print_grammar
   .. automethod:: context
   .. automethod:: tokens
   .. automethod:: tree

.. autoclass:: AnnotatedTreeWalker

   .. automethod:: load
   .. automethod:: save
   .. automethod:: catchall
   .. automethod:: register
   .. automethod:: RECOURSE_CHILDREN
   .. automethod:: TREE_CATCHALL
   .. automethod:: TEXT_CATCHALL

LLVM support
------------

This *very experimental* module provides a commodity class to play with `LLVM <https://llvm.org/>`_ IR language.

.. currentmodule:: liblet.llvm

.. autoclass:: LLVM

   .. automethod:: new_variable
   .. automethod:: new_label
   .. automethod:: append_code
   .. automethod:: write_and_compile
   .. automethod:: control_flow_graph
   .. automethod:: mem2reg

Rich display
------------

.. currentmodule:: liblet.display

.. autoclass:: Graph

   .. automethod:: neighbors
   .. automethod:: from_adjdict

.. autoclass:: Tree

   .. automethod:: from_lol
   .. automethod:: from_pyast
   .. automethod:: with_threads

.. autoclass:: ProductionGraph

.. autoclass:: StateTransitionGraph

   .. automethod:: from_automaton


Utilities and decorators
------------------------

.. currentmodule:: liblet.utils

.. autoclass:: Queue
.. autoclass:: Stack
.. autoclass:: Table
.. autoclass:: AttrDict
.. autofunction:: warn
.. autofunction:: union_of

.. currentmodule:: liblet.decorators

.. autofunction:: closure

.. autofunction:: show_calls
