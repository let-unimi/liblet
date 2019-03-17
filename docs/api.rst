.. _api:

API
===

Productions and Grammars
------------------------

.. testsetup:: *

   from liblet import Production

.. module:: liblet.grammar

The basic building block of a *grammar* is a *production* represented by the following class.

.. autoclass:: Production

A convenience method is provided to obtain productions from a suitable string
representation of them.

.. automethod:: Production.from_string

A grammar can be represented by the following class, that can be instantiated
given the usual formal definition of a grammar as a tuple.

.. autoclass:: Grammar

Even in the case of grammars, a convenience method is provided to build a
grammar from a suitable string representation. Once the productions are obtained
with :func:`Production.from_grammar`, the remaining parameters are
conventionally inferred as detailed below.

.. automethod:: Grammar.from_string

A couple of utility methods are provided:

.. automethod:: Grammar.rhs

.. automethod:: Grammar.all_terminals

Derivations
-----------

Once a grammar has been defined, one can build derivations with the help of the
following class.

.. autoclass:: Derivation

   .. automethod:: step
   
   .. automethod:: rightmost

   .. automethod:: leftmost

   .. automethod:: possible_steps

Rich dislpay
------------

.. module:: liblet.display

.. autoclass:: Tree

.. autoclass:: Graph

.. autoclass:: ProductionGraph

.. autoclass:: StateTransitionGraph


