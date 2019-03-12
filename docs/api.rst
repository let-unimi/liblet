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

A convenience method is provided to obtain productions from a string of given format.

.. automethod:: Production.from_string

.. autoclass:: Grammar

   .. automethod:: from_string

Derivations
-----------

.. autoclass:: Derivation

