.. _api:

API
===

.. testsetup:: *

   from liblet import Production, closure, show_calls


Productions, Grammars and Derivations
-------------------------------------

.. currentmodule:: liblet.grammar

The basic building block of a *grammar* is a *production* represented by the following class.

.. autoclass:: Production

   A convenience method is provided to obtain productions from a suitable string
   representation of them.
   
   .. automethod:: from_string
   
   A grammar can be represented by the following class, that can be instantiated
   given the usual formal definition of a grammar as a tuple.

.. autoclass:: Grammar

   Even in the case of grammars, a convenience method is provided to build a
   grammar from a suitable string representation. Once the productions are obtained
   with :func:`Production.from_grammar`, the remaining parameters are
   conventionally inferred as detailed below.
   
   .. automethod:: from_string
   
   An utility method is provided to enumerate alternatives for a given *lefthand* side:
   
   .. automethod:: alternatives

Once a grammar has been defined, one can build derivations with the help of the
following class.

.. autoclass:: Derivation

   .. automethod:: step
   
   .. automethod:: leftmost

   .. automethod:: rightmost

   .. automethod:: possible_steps

   .. automethod:: steps

   .. automethod:: sentential_form


Transitions and Automata
------------------------

.. currentmodule:: liblet.automaton

If one wants to restrict the attention to *regular grammars* the library
provides a basic class to represent a *transition*

.. autoclass:: Transition

Moreover a class to describe (*nondeterministic*) *finite state automata* is
provided.

.. autoclass:: Automaton



Rich dislpay
------------

.. currentmodule:: liblet.display

.. autoclass:: Tree

.. autoclass:: Graph

.. autoclass:: ProductionGraph

.. autoclass:: StateTransitionGraph


Utilities and decorators
------------------------

.. currentmodule:: liblet.utils

.. currentmodule:: liblet.decorators

.. autofunction:: closure 

.. autofunction:: show_calls