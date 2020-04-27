.. _examples:

Examples
========

To give a thorough example of what the library allows to implement, in
this `Jupyter <https://jupyter.org/>`__ session we follow rather
faitfully some Sections of `Parsing
Techniques <https://dickgrune.com//Books/PTAPG_2nd_Edition/>`__, an
eccellent book on parsing by Dick Grune and Ceriel J.H. Jacobs. We can
omit many details (such as defintions, proofs, careful algorithm
explanations…) but the interested reader can still find in such text a
very precise, clear and conceputal description of the ideas behind the
code implemented in the following examples.

Type 1 grammars and production graphs
-------------------------------------

Let’s start defining a *monotonic* grammar for :math:`a^nb^nc^n`

.. code:: ipython3

    from liblet import Grammar
    
    G = Grammar.from_string("""
    S -> a b c
    S -> a S Q
    b Q c -> b b c c
    c Q -> Q c
    """, False)
    
    G




.. parsed-literal::

    Grammar(N={Q, S}, T={a, b, c}, P=(S -> a b c, S -> a S Q, b Q c -> b b c c, c Q -> Q c), S=S)



It can be convenient to show the productions as a table, with numbered
rows.

.. code:: ipython3

    from liblet import iter2table
    
    iter2table(G.P)




.. raw:: html

    <style>td, th {border: 1pt solid lightgray !important ;}</style><table><tr><th style="text-align:left">0<td style="text-align:left"><pre>S -&gt; a b c</pre>
    <tr><th style="text-align:left">1<td style="text-align:left"><pre>S -&gt; a S Q</pre>
    <tr><th style="text-align:left">2<td style="text-align:left"><pre>b Q c -&gt; b b c c</pre>
    <tr><th style="text-align:left">3<td style="text-align:left"><pre>c Q -&gt; Q c</pre></table>



It’s now time to create a *derivation* of :math:`a^2b^2c^2`

.. code:: ipython3

    from liblet import Derivation
    
    d = Derivation(G).step(1, 0).step(0, 1).step(3, 3).step(2, 2)
    d




.. parsed-literal::

    S -> a S Q -> a a b c Q -> a a b Q c -> a a b b c c



It can be quite illuminating to see the *production graph* for such
derivation

.. code:: ipython3

    from liblet import ProductionGraph
    
    ProductionGraph(d)




.. image:: examples_files/examples_8_0.svg



Context-free grammars and ambiguity
-----------------------------------

Assume we want to experiment with an ambiguous grammar and look for two
different leftmost derivation of the same sentence.

To this aim, let’s consider the following grammar and a short derivation
leading to and addition of three terminals

.. code:: ipython3

    G = Grammar.from_string("""
    E -> E + E
    E -> E * E
    E -> i
    """)
    
    d = Derivation(G).step(0, 0).step(0, 0)
    d




.. parsed-literal::

    E -> E + E -> E + E + E



What are the possible steps at this point? The ``possible_steps`` method
comes in handy, here is a (numbered) table of pairs :math:`(p, q)` where
:math:`p` is production number and :math:`q` the position of the
nonterminal that can be substituted:

.. code:: ipython3

    possible_steps = list(d.possible_steps())
    iter2table(possible_steps)




.. raw:: html

    <style>td, th {border: 1pt solid lightgray !important ;}</style><table><tr><th style="text-align:left">0<td style="text-align:left"><pre>(0, 0)</pre>
    <tr><th style="text-align:left">1<td style="text-align:left"><pre>(0, 2)</pre>
    <tr><th style="text-align:left">2<td style="text-align:left"><pre>(0, 4)</pre>
    <tr><th style="text-align:left">3<td style="text-align:left"><pre>(1, 0)</pre>
    <tr><th style="text-align:left">4<td style="text-align:left"><pre>(1, 2)</pre>
    <tr><th style="text-align:left">5<td style="text-align:left"><pre>(1, 4)</pre>
    <tr><th style="text-align:left">6<td style="text-align:left"><pre>(2, 0)</pre>
    <tr><th style="text-align:left">7<td style="text-align:left"><pre>(2, 2)</pre>
    <tr><th style="text-align:left">8<td style="text-align:left"><pre>(2, 4)</pre></table>



If we look for just for leftmost derivations among the
:math:`(p, q)`\ s, we must keep just the :math:`p`\ s corresponding to
the :math:`q`\ s equal to the minimum of the possible :math:`q` values.
The following function can be used to such aim:

.. code:: ipython3

    from operator import itemgetter
    
    def filter_leftmost_prods(possible_steps):
        possible_steps = list(possible_steps)
        if possible_steps:
            min_q = min(possible_steps, key = itemgetter(1))[1]
            return map(itemgetter(0), filter(lambda ps: ps[1] == min_q, possible_steps))
        return tuple()
    
    list(filter_leftmost_prods(possible_steps))




.. parsed-literal::

    [0, 1, 2]



Now, using a ``Queue`` we can enumerate all the leftmost productions, we
can have a fancy generator that returns a new derivation each time
``next`` is called on it:

.. code:: ipython3

    from liblet import Queue
    
    def derivation_generator(G):
        Q = Queue([Derivation(G)])
        while Q:
            derivation = Q.dequeue()
            if set(derivation.sentential_form()) <= G.T: 
                yield derivation
            for nprod in filter_leftmost_prods(derivation.possible_steps()):
                Q.enqueue(derivation.leftmost(nprod))

Let’s collect the first 10 derivations

.. code:: ipython3

    derivation = derivation_generator(G)
    D = [next(derivation) for _ in range(10)]
    iter2table(D)




.. raw:: html

    <style>td, th {border: 1pt solid lightgray !important ;}</style><table><tr><th style="text-align:left">0<td style="text-align:left"><pre>E -&gt; i</pre>
    <tr><th style="text-align:left">1<td style="text-align:left"><pre>E -&gt; E + E -&gt; i + E -&gt; i + i</pre>
    <tr><th style="text-align:left">2<td style="text-align:left"><pre>E -&gt; E * E -&gt; i * E -&gt; i * i</pre>
    <tr><th style="text-align:left">3<td style="text-align:left"><pre>E -&gt; E + E -&gt; E + E + E -&gt; i + E + E -&gt; i + i + E -&gt; i + i + i</pre>
    <tr><th style="text-align:left">4<td style="text-align:left"><pre>E -&gt; E + E -&gt; E * E + E -&gt; i * E + E -&gt; i * i + E -&gt; i * i + i</pre>
    <tr><th style="text-align:left">5<td style="text-align:left"><pre>E -&gt; E + E -&gt; i + E -&gt; i + E + E -&gt; i + i + E -&gt; i + i + i</pre>
    <tr><th style="text-align:left">6<td style="text-align:left"><pre>E -&gt; E + E -&gt; i + E -&gt; i + E * E -&gt; i + i * E -&gt; i + i * i</pre>
    <tr><th style="text-align:left">7<td style="text-align:left"><pre>E -&gt; E * E -&gt; E + E * E -&gt; i + E * E -&gt; i + i * E -&gt; i + i * i</pre>
    <tr><th style="text-align:left">8<td style="text-align:left"><pre>E -&gt; E * E -&gt; E * E * E -&gt; i * E * E -&gt; i * i * E -&gt; i * i * i</pre>
    <tr><th style="text-align:left">9<td style="text-align:left"><pre>E -&gt; E * E -&gt; i * E -&gt; i * E + E -&gt; i * i + E -&gt; i * i + i</pre></table>



As one can easily see, derivations 6 and 7 produce the same sentence
``i + i * i`` but evidently with two different leftmost derivations. We
can give a look at the production graphs to better see what is
happening.

.. code:: ipython3

    from liblet import side_by_side
    
    side_by_side(ProductionGraph(D[6]), ProductionGraph(D[7]))




.. raw:: html

    <div><?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
     "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <!-- Generated by graphviz version 2.43.0 (0)
     -->
    <!-- Title: %3 Pages: 1 -->
    <svg width="127pt" height="150pt"
     viewBox="0.00 0.00 126.55 150.00" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <g id="graph0" class="graph" transform="scale(1 1) rotate(0) translate(4 146)">
    <title>%3</title>
    <polygon fill="white" stroke="transparent" points="-4,4 -4,-146 122.55,-146 122.55,4 -4,4"/>
    <!-- &#45;4859444877843755635 -->
    <g id="node1" class="node">
    <title>&#45;4859444877843755635</title>
    <path fill="none" stroke="black" stroke-width="0.25" d="M44.96,-142C44.96,-142 39.59,-142 39.59,-142 36.9,-142 34.22,-139.31 34.22,-136.63 34.22,-136.63 34.22,-125.37 34.22,-125.37 34.22,-122.69 36.9,-120 39.59,-120 39.59,-120 44.96,-120 44.96,-120 47.65,-120 50.33,-122.69 50.33,-125.37 50.33,-125.37 50.33,-136.63 50.33,-136.63 50.33,-139.31 47.65,-142 44.96,-142"/>
    <text text-anchor="middle" x="42.28" y="-126.8" font-family="Times,serif" font-size="14.00">E</text>
    </g>
    <!-- &#45;4859443616646756812 -->
    <g id="node2" class="node">
    <title>&#45;4859443616646756812</title>
    <path fill="none" stroke="black" stroke-width="0.25" d="M10.96,-102C10.96,-102 5.59,-102 5.59,-102 2.9,-102 0.22,-99.31 0.22,-96.63 0.22,-96.63 0.22,-85.37 0.22,-85.37 0.22,-82.69 2.9,-80 5.59,-80 5.59,-80 10.96,-80 10.96,-80 13.65,-80 16.33,-82.69 16.33,-85.37 16.33,-85.37 16.33,-96.63 16.33,-96.63 16.33,-99.31 13.65,-102 10.96,-102"/>
    <text text-anchor="middle" x="8.28" y="-86.8" font-family="Times,serif" font-size="14.00">E</text>
    </g>
    <!-- &#45;4859444877843755635&#45;&gt;&#45;4859443616646756812 -->
    <g id="edge1" class="edge">
    <title>&#45;4859444877843755635&#45;&gt;&#45;4859443616646756812</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M34.05,-120.8C28.7,-114.83 21.76,-107.07 16.43,-101.11"/>
    </g>
    <!-- &#45;3631962049399463494 -->
    <g id="node3" class="node">
    <title>&#45;3631962049399463494</title>
    <path fill="none" stroke="black" stroke-width="1.25" d="M44.91,-102C44.91,-102 39.64,-102 39.64,-102 37.01,-102 34.38,-99.37 34.38,-96.74 34.38,-96.74 34.38,-85.26 34.38,-85.26 34.38,-82.63 37.01,-80 39.64,-80 39.64,-80 44.91,-80 44.91,-80 47.54,-80 50.17,-82.63 50.17,-85.26 50.17,-85.26 50.17,-96.74 50.17,-96.74 50.17,-99.37 47.54,-102 44.91,-102"/>
    <text text-anchor="middle" x="42.28" y="-86.8" font-family="Times,serif" font-size="14.00">+</text>
    </g>
    <!-- &#45;4859444877843755635&#45;&gt;&#45;3631962049399463494 -->
    <g id="edge2" class="edge">
    <title>&#45;4859444877843755635&#45;&gt;&#45;3631962049399463494</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M42.28,-119.62C42.28,-114.17 42.28,-107.52 42.28,-102.11"/>
    </g>
    <!-- &#45;4859443616644426714 -->
    <g id="node4" class="node">
    <title>&#45;4859443616644426714</title>
    <path fill="none" stroke="black" stroke-width="0.25" d="M78.96,-102C78.96,-102 73.59,-102 73.59,-102 70.9,-102 68.22,-99.31 68.22,-96.63 68.22,-96.63 68.22,-85.37 68.22,-85.37 68.22,-82.69 70.9,-80 73.59,-80 73.59,-80 78.96,-80 78.96,-80 81.65,-80 84.33,-82.69 84.33,-85.37 84.33,-85.37 84.33,-96.63 84.33,-96.63 84.33,-99.31 81.65,-102 78.96,-102"/>
    <text text-anchor="middle" x="76.28" y="-86.8" font-family="Times,serif" font-size="14.00">E</text>
    </g>
    <!-- &#45;4859444877843755635&#45;&gt;&#45;4859443616644426714 -->
    <g id="edge3" class="edge">
    <title>&#45;4859444877843755635&#45;&gt;&#45;4859443616644426714</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M50.51,-120.8C55.85,-114.83 62.79,-107.07 68.12,-101.11"/>
    </g>
    <!-- &#45;4859443616646756812&#45;&gt;&#45;3631962049399463494 -->
    <!-- 3166482649488112007 -->
    <g id="node5" class="node">
    <title>3166482649488112007</title>
    <path fill="none" stroke="black" stroke-width="1.25" d="M10.24,-62C10.24,-62 6.31,-62 6.31,-62 4.35,-62 2.39,-60.04 2.39,-58.07 2.39,-58.07 2.39,-43.93 2.39,-43.93 2.39,-41.96 4.35,-40 6.31,-40 6.31,-40 10.24,-40 10.24,-40 12.2,-40 14.17,-41.96 14.17,-43.93 14.17,-43.93 14.17,-58.07 14.17,-58.07 14.17,-60.04 12.2,-62 10.24,-62"/>
    <text text-anchor="middle" x="8.28" y="-46.8" font-family="Times,serif" font-size="14.00">i</text>
    </g>
    <!-- &#45;4859443616646756812&#45;&gt;3166482649488112007 -->
    <g id="edge6" class="edge">
    <title>&#45;4859443616646756812&#45;&gt;3166482649488112007</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M8.28,-79.62C8.28,-74.17 8.28,-67.52 8.28,-62.11"/>
    </g>
    <!-- &#45;3631962049399463494&#45;&gt;&#45;4859443616644426714 -->
    <!-- &#45;4859446139040754458 -->
    <g id="node6" class="node">
    <title>&#45;4859446139040754458</title>
    <path fill="none" stroke="black" stroke-width="0.25" d="M44.96,-62C44.96,-62 39.59,-62 39.59,-62 36.9,-62 34.22,-59.31 34.22,-56.63 34.22,-56.63 34.22,-45.37 34.22,-45.37 34.22,-42.69 36.9,-40 39.59,-40 39.59,-40 44.96,-40 44.96,-40 47.65,-40 50.33,-42.69 50.33,-45.37 50.33,-45.37 50.33,-56.63 50.33,-56.63 50.33,-59.31 47.65,-62 44.96,-62"/>
    <text text-anchor="middle" x="42.28" y="-46.8" font-family="Times,serif" font-size="14.00">E</text>
    </g>
    <!-- &#45;4859443616644426714&#45;&gt;&#45;4859446139040754458 -->
    <g id="edge7" class="edge">
    <title>&#45;4859443616644426714&#45;&gt;&#45;4859446139040754458</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M68.05,-80.8C62.7,-74.83 55.76,-67.07 50.43,-61.11"/>
    </g>
    <!-- 5450393231786277370 -->
    <g id="node7" class="node">
    <title>5450393231786277370</title>
    <path fill="none" stroke="black" stroke-width="1.25" d="M78.78,-62C78.78,-62 73.78,-62 73.78,-62 71.28,-62 68.78,-59.5 68.78,-57 68.78,-57 68.78,-45 68.78,-45 68.78,-42.5 71.28,-40 73.78,-40 73.78,-40 78.78,-40 78.78,-40 81.28,-40 83.78,-42.5 83.78,-45 83.78,-45 83.78,-57 83.78,-57 83.78,-59.5 81.28,-62 78.78,-62"/>
    <text text-anchor="middle" x="76.28" y="-46.8" font-family="Times,serif" font-size="14.00">*</text>
    </g>
    <!-- &#45;4859443616644426714&#45;&gt;5450393231786277370 -->
    <g id="edge8" class="edge">
    <title>&#45;4859443616644426714&#45;&gt;5450393231786277370</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M76.28,-79.62C76.28,-74.17 76.28,-67.52 76.28,-62.11"/>
    </g>
    <!-- &#45;4859446139043084556 -->
    <g id="node8" class="node">
    <title>&#45;4859446139043084556</title>
    <path fill="none" stroke="black" stroke-width="0.25" d="M112.96,-62C112.96,-62 107.59,-62 107.59,-62 104.9,-62 102.22,-59.31 102.22,-56.63 102.22,-56.63 102.22,-45.37 102.22,-45.37 102.22,-42.69 104.9,-40 107.59,-40 107.59,-40 112.96,-40 112.96,-40 115.65,-40 118.33,-42.69 118.33,-45.37 118.33,-45.37 118.33,-56.63 118.33,-56.63 118.33,-59.31 115.65,-62 112.96,-62"/>
    <text text-anchor="middle" x="110.28" y="-46.8" font-family="Times,serif" font-size="14.00">E</text>
    </g>
    <!-- &#45;4859443616644426714&#45;&gt;&#45;4859446139043084556 -->
    <g id="edge9" class="edge">
    <title>&#45;4859443616644426714&#45;&gt;&#45;4859446139043084556</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M84.51,-80.8C89.85,-74.83 96.79,-67.07 102.12,-61.11"/>
    </g>
    <!-- &#45;4859446139040754458&#45;&gt;5450393231786277370 -->
    <!-- 3166480127094114361 -->
    <g id="node9" class="node">
    <title>3166480127094114361</title>
    <path fill="none" stroke="black" stroke-width="1.25" d="M44.24,-22C44.24,-22 40.31,-22 40.31,-22 38.35,-22 36.39,-20.04 36.39,-18.07 36.39,-18.07 36.39,-3.93 36.39,-3.93 36.39,-1.96 38.35,0 40.31,0 40.31,0 44.24,0 44.24,0 46.2,0 48.17,-1.96 48.17,-3.93 48.17,-3.93 48.17,-18.07 48.17,-18.07 48.17,-20.04 46.2,-22 44.24,-22"/>
    <text text-anchor="middle" x="42.28" y="-6.8" font-family="Times,serif" font-size="14.00">i</text>
    </g>
    <!-- &#45;4859446139040754458&#45;&gt;3166480127094114361 -->
    <g id="edge12" class="edge">
    <title>&#45;4859446139040754458&#45;&gt;3166480127094114361</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M42.28,-39.62C42.28,-34.17 42.28,-27.52 42.28,-22.11"/>
    </g>
    <!-- 5450393231786277370&#45;&gt;&#45;4859446139043084556 -->
    <!-- 3166481388291113184 -->
    <g id="node10" class="node">
    <title>3166481388291113184</title>
    <path fill="none" stroke="black" stroke-width="1.25" d="M112.24,-22C112.24,-22 108.31,-22 108.31,-22 106.35,-22 104.39,-20.04 104.39,-18.07 104.39,-18.07 104.39,-3.93 104.39,-3.93 104.39,-1.96 106.35,0 108.31,0 108.31,0 112.24,0 112.24,0 114.2,0 116.17,-1.96 116.17,-3.93 116.17,-3.93 116.17,-18.07 116.17,-18.07 116.17,-20.04 114.2,-22 112.24,-22"/>
    <text text-anchor="middle" x="110.28" y="-6.8" font-family="Times,serif" font-size="14.00">i</text>
    </g>
    <!-- &#45;4859446139043084556&#45;&gt;3166481388291113184 -->
    <g id="edge13" class="edge">
    <title>&#45;4859446139043084556&#45;&gt;3166481388291113184</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M110.28,-39.62C110.28,-34.17 110.28,-27.52 110.28,-22.11"/>
    </g>
    </g>
    </svg>
     <?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
     "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <!-- Generated by graphviz version 2.43.0 (0)
     -->
    <!-- Title: %3 Pages: 1 -->
    <svg width="127pt" height="150pt"
     viewBox="0.00 0.00 126.55 150.00" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <g id="graph0" class="graph" transform="scale(1 1) rotate(0) translate(4 146)">
    <title>%3</title>
    <polygon fill="white" stroke="transparent" points="-4,4 -4,-146 122.55,-146 122.55,4 -4,4"/>
    <!-- &#45;4859444877843755635 -->
    <g id="node1" class="node">
    <title>&#45;4859444877843755635</title>
    <path fill="none" stroke="black" stroke-width="0.25" d="M78.96,-142C78.96,-142 73.59,-142 73.59,-142 70.9,-142 68.22,-139.31 68.22,-136.63 68.22,-136.63 68.22,-125.37 68.22,-125.37 68.22,-122.69 70.9,-120 73.59,-120 73.59,-120 78.96,-120 78.96,-120 81.65,-120 84.33,-122.69 84.33,-125.37 84.33,-125.37 84.33,-136.63 84.33,-136.63 84.33,-139.31 81.65,-142 78.96,-142"/>
    <text text-anchor="middle" x="76.28" y="-126.8" font-family="Times,serif" font-size="14.00">E</text>
    </g>
    <!-- &#45;4859443616646756812 -->
    <g id="node2" class="node">
    <title>&#45;4859443616646756812</title>
    <path fill="none" stroke="black" stroke-width="0.25" d="M44.96,-102C44.96,-102 39.59,-102 39.59,-102 36.9,-102 34.22,-99.31 34.22,-96.63 34.22,-96.63 34.22,-85.37 34.22,-85.37 34.22,-82.69 36.9,-80 39.59,-80 39.59,-80 44.96,-80 44.96,-80 47.65,-80 50.33,-82.69 50.33,-85.37 50.33,-85.37 50.33,-96.63 50.33,-96.63 50.33,-99.31 47.65,-102 44.96,-102"/>
    <text text-anchor="middle" x="42.28" y="-86.8" font-family="Times,serif" font-size="14.00">E</text>
    </g>
    <!-- &#45;4859444877843755635&#45;&gt;&#45;4859443616646756812 -->
    <g id="edge1" class="edge">
    <title>&#45;4859444877843755635&#45;&gt;&#45;4859443616646756812</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M68.05,-120.8C62.7,-114.83 55.76,-107.07 50.43,-101.11"/>
    </g>
    <!-- 5450390709392279724 -->
    <g id="node3" class="node">
    <title>5450390709392279724</title>
    <path fill="none" stroke="black" stroke-width="1.25" d="M78.78,-102C78.78,-102 73.78,-102 73.78,-102 71.28,-102 68.78,-99.5 68.78,-97 68.78,-97 68.78,-85 68.78,-85 68.78,-82.5 71.28,-80 73.78,-80 73.78,-80 78.78,-80 78.78,-80 81.28,-80 83.78,-82.5 83.78,-85 83.78,-85 83.78,-97 83.78,-97 83.78,-99.5 81.28,-102 78.78,-102"/>
    <text text-anchor="middle" x="76.28" y="-86.8" font-family="Times,serif" font-size="14.00">*</text>
    </g>
    <!-- &#45;4859444877843755635&#45;&gt;5450390709392279724 -->
    <g id="edge2" class="edge">
    <title>&#45;4859444877843755635&#45;&gt;5450390709392279724</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M76.28,-119.62C76.28,-114.17 76.28,-107.52 76.28,-102.11"/>
    </g>
    <!-- &#45;4859443616644426714 -->
    <g id="node4" class="node">
    <title>&#45;4859443616644426714</title>
    <path fill="none" stroke="black" stroke-width="0.25" d="M112.96,-102C112.96,-102 107.59,-102 107.59,-102 104.9,-102 102.22,-99.31 102.22,-96.63 102.22,-96.63 102.22,-85.37 102.22,-85.37 102.22,-82.69 104.9,-80 107.59,-80 107.59,-80 112.96,-80 112.96,-80 115.65,-80 118.33,-82.69 118.33,-85.37 118.33,-85.37 118.33,-96.63 118.33,-96.63 118.33,-99.31 115.65,-102 112.96,-102"/>
    <text text-anchor="middle" x="110.28" y="-86.8" font-family="Times,serif" font-size="14.00">E</text>
    </g>
    <!-- &#45;4859444877843755635&#45;&gt;&#45;4859443616644426714 -->
    <g id="edge3" class="edge">
    <title>&#45;4859444877843755635&#45;&gt;&#45;4859443616644426714</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M84.51,-120.8C89.85,-114.83 96.79,-107.07 102.12,-101.11"/>
    </g>
    <!-- &#45;4859443616646756812&#45;&gt;5450390709392279724 -->
    <!-- &#45;4859447400237753281 -->
    <g id="node5" class="node">
    <title>&#45;4859447400237753281</title>
    <path fill="none" stroke="black" stroke-width="0.25" d="M10.96,-62C10.96,-62 5.59,-62 5.59,-62 2.9,-62 0.22,-59.31 0.22,-56.63 0.22,-56.63 0.22,-45.37 0.22,-45.37 0.22,-42.69 2.9,-40 5.59,-40 5.59,-40 10.96,-40 10.96,-40 13.65,-40 16.33,-42.69 16.33,-45.37 16.33,-45.37 16.33,-56.63 16.33,-56.63 16.33,-59.31 13.65,-62 10.96,-62"/>
    <text text-anchor="middle" x="8.28" y="-46.8" font-family="Times,serif" font-size="14.00">E</text>
    </g>
    <!-- &#45;4859443616646756812&#45;&gt;&#45;4859447400237753281 -->
    <g id="edge6" class="edge">
    <title>&#45;4859443616646756812&#45;&gt;&#45;4859447400237753281</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M34.05,-80.8C28.7,-74.83 21.76,-67.07 16.43,-61.11"/>
    </g>
    <!-- &#45;3631963310598792415 -->
    <g id="node6" class="node">
    <title>&#45;3631963310598792415</title>
    <path fill="none" stroke="black" stroke-width="1.25" d="M44.91,-62C44.91,-62 39.64,-62 39.64,-62 37.01,-62 34.38,-59.37 34.38,-56.74 34.38,-56.74 34.38,-45.26 34.38,-45.26 34.38,-42.63 37.01,-40 39.64,-40 39.64,-40 44.91,-40 44.91,-40 47.54,-40 50.17,-42.63 50.17,-45.26 50.17,-45.26 50.17,-56.74 50.17,-56.74 50.17,-59.37 47.54,-62 44.91,-62"/>
    <text text-anchor="middle" x="42.28" y="-46.8" font-family="Times,serif" font-size="14.00">+</text>
    </g>
    <!-- &#45;4859443616646756812&#45;&gt;&#45;3631963310598792415 -->
    <g id="edge7" class="edge">
    <title>&#45;4859443616646756812&#45;&gt;&#45;3631963310598792415</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M42.28,-79.62C42.28,-74.17 42.28,-67.52 42.28,-62.11"/>
    </g>
    <!-- &#45;4859447400235423183 -->
    <g id="node7" class="node">
    <title>&#45;4859447400235423183</title>
    <path fill="none" stroke="black" stroke-width="0.25" d="M78.96,-62C78.96,-62 73.59,-62 73.59,-62 70.9,-62 68.22,-59.31 68.22,-56.63 68.22,-56.63 68.22,-45.37 68.22,-45.37 68.22,-42.69 70.9,-40 73.59,-40 73.59,-40 78.96,-40 78.96,-40 81.65,-40 84.33,-42.69 84.33,-45.37 84.33,-45.37 84.33,-56.63 84.33,-56.63 84.33,-59.31 81.65,-62 78.96,-62"/>
    <text text-anchor="middle" x="76.28" y="-46.8" font-family="Times,serif" font-size="14.00">E</text>
    </g>
    <!-- &#45;4859443616646756812&#45;&gt;&#45;4859447400235423183 -->
    <g id="edge8" class="edge">
    <title>&#45;4859443616646756812&#45;&gt;&#45;4859447400235423183</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M50.51,-80.8C55.85,-74.83 62.79,-67.07 68.12,-61.11"/>
    </g>
    <!-- 5450390709392279724&#45;&gt;&#45;4859443616644426714 -->
    <!-- 3166481388291113184 -->
    <g id="node10" class="node">
    <title>3166481388291113184</title>
    <path fill="none" stroke="black" stroke-width="1.25" d="M112.24,-62C112.24,-62 108.31,-62 108.31,-62 106.35,-62 104.39,-60.04 104.39,-58.07 104.39,-58.07 104.39,-43.93 104.39,-43.93 104.39,-41.96 106.35,-40 108.31,-40 108.31,-40 112.24,-40 112.24,-40 114.2,-40 116.17,-41.96 116.17,-43.93 116.17,-43.93 116.17,-58.07 116.17,-58.07 116.17,-60.04 114.2,-62 112.24,-62"/>
    <text text-anchor="middle" x="110.28" y="-46.8" font-family="Times,serif" font-size="14.00">i</text>
    </g>
    <!-- &#45;4859443616644426714&#45;&gt;3166481388291113184 -->
    <g id="edge13" class="edge">
    <title>&#45;4859443616644426714&#45;&gt;3166481388291113184</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M110.28,-79.62C110.28,-74.17 110.28,-67.52 110.28,-62.11"/>
    </g>
    <!-- &#45;4859447400237753281&#45;&gt;&#45;3631963310598792415 -->
    <!-- 3166483910685110830 -->
    <g id="node8" class="node">
    <title>3166483910685110830</title>
    <path fill="none" stroke="black" stroke-width="1.25" d="M10.24,-22C10.24,-22 6.31,-22 6.31,-22 4.35,-22 2.39,-20.04 2.39,-18.07 2.39,-18.07 2.39,-3.93 2.39,-3.93 2.39,-1.96 4.35,0 6.31,0 6.31,0 10.24,0 10.24,0 12.2,0 14.17,-1.96 14.17,-3.93 14.17,-3.93 14.17,-18.07 14.17,-18.07 14.17,-20.04 12.2,-22 10.24,-22"/>
    <text text-anchor="middle" x="8.28" y="-6.8" font-family="Times,serif" font-size="14.00">i</text>
    </g>
    <!-- &#45;4859447400237753281&#45;&gt;3166483910685110830 -->
    <g id="edge11" class="edge">
    <title>&#45;4859447400237753281&#45;&gt;3166483910685110830</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M8.28,-39.62C8.28,-34.17 8.28,-27.52 8.28,-22.11"/>
    </g>
    <!-- &#45;3631963310598792415&#45;&gt;&#45;4859447400235423183 -->
    <!-- 3166480127094114361 -->
    <g id="node9" class="node">
    <title>3166480127094114361</title>
    <path fill="none" stroke="black" stroke-width="1.25" d="M78.24,-22C78.24,-22 74.31,-22 74.31,-22 72.35,-22 70.39,-20.04 70.39,-18.07 70.39,-18.07 70.39,-3.93 70.39,-3.93 70.39,-1.96 72.35,0 74.31,0 74.31,0 78.24,0 78.24,0 80.2,0 82.17,-1.96 82.17,-3.93 82.17,-3.93 82.17,-18.07 82.17,-18.07 82.17,-20.04 80.2,-22 78.24,-22"/>
    <text text-anchor="middle" x="76.28" y="-6.8" font-family="Times,serif" font-size="14.00">i</text>
    </g>
    <!-- &#45;4859447400235423183&#45;&gt;3166480127094114361 -->
    <g id="edge12" class="edge">
    <title>&#45;4859447400235423183&#45;&gt;3166480127094114361</title>
    <path fill="none" stroke="black" stroke-width="0.5" d="M76.28,-39.62C76.28,-34.17 76.28,-27.52 76.28,-22.11"/>
    </g>
    </g>
    </svg>
    </div>



Hygiene in Context-Free Grammars
--------------------------------

First of all, let’s start with a series of techniques to clean a
*context-free* grammar by removing *unreachable*, *non-productive*, and
*undefined* symbols. Let’s start with the *context-free* grammar
:math:`G` of Figure 2.25 at page 49 of `Parsing
Techniques <https://dickgrune.com//Books/PTAPG_2nd_Edition/>`__, in
particular we’ll be following the flow of Sections 2.9.1, 2.9.2 and
2.9.5.

.. code:: ipython3

    G = Grammar.from_string("""
    S -> A B | D E
    A -> a
    B -> b C
    C -> c
    D -> d F 
    E -> e 
    F -> f D
    """)

We can use the ``@closure`` decorator to obtain the *productive* symbols
by extending at every round the set ``prod`` of productive symbols as
``{A for A, α in G.P if set(α) <= prod}``, that is taking all the
left-hand sides of productions whose left-hand sides are in turn made of
productive symbols.

.. code:: ipython3

    from liblet import closure
    
    def find_productive(G):
        @closure
        def find(prod):
            return prod | {A for A, α in G.P if set(α) <= prod}
        return set(find(G.T))

.. code:: ipython3

    find_productive(G)




.. parsed-literal::

    {'A', 'B', 'C', 'E', 'S', 'a', 'b', 'c', 'd', 'e', 'f'}



Similarly, we can obtain the *reachable* symbols by extending at every
round the set ``reach`` of reachable symbols as
``union_of(set(α) for A, α in G.P if A in reach)}``, that is taking the
union all the left-hand sides of productions whose left-hand sides are
in turn reachable.

.. code:: ipython3

    from liblet import union_of
    
    def find_reachable(G):
        @closure
        def find(reach, G):
            return reach | union_of(set(α) for A, α in G.P if A in reach)
        return find({G.S}, G)   

.. code:: ipython3

    find_reachable(G)




.. parsed-literal::

    {'A', 'B', 'C', 'D', 'E', 'F', 'S', 'a', 'b', 'c', 'd', 'e', 'f'}



To clean the grammar one has first to eliminate the non-productive
symbols and the the non-reachable onse (as acting in the reverse order
can leave around non-reachable symbols after the first removal).

.. code:: ipython3

    def remove_unproductive_unreachable(G):
        Gp = G.restrict_to(find_productive(G))
        return Gp.restrict_to(find_reachable(Gp))

.. code:: ipython3

    remove_unproductive_unreachable(G)




.. parsed-literal::

    Grammar(N={A, B, C, S}, T={a, b, c}, P=(S -> A B, A -> a, B -> b C, C -> c), S=S)



To remove *undefined* nonterminals is easy, it’s enough to collect the
ones appearing as left-hand side in some production and throw away the
others

.. code:: ipython3

    def remove_undefined(G):
        return G.restrict_to({A for A, α in G.P} | G.T)

Given that ``Grammar.from_string`` considers nonterminal just the
symbols on the left-hand sides, to check that the last method works we
need to build a grammar in another way:

.. code:: ipython3

    from liblet import Production
    
    Gu = Grammar({'S', 'T'}, {'s'}, (Production('S', ('s',)),), 'S')
    Gu




.. parsed-literal::

    Grammar(N={S, T}, T={s}, P=(S -> s,), S=S)



.. code:: ipython3

    remove_undefined(Gu)




.. parsed-literal::

    Grammar(N={S}, T={s}, P=(S -> s,), S=S)



Observe that undefined symbols are non-productive, hence
``remove_unproductive_unreachable`` will take implicitly care of them.

The Chomsky Normal Form
-----------------------

Now that the grammar contains only defined, productive and reachable
symbols, to get to the CHomsky normal form we need to take care of
ε-rules and unit rules (following Section 4.2.3 of `Parsing
Techniques <https://dickgrune.com//Books/PTAPG_2nd_Edition/>`__).

Elimination of ε-rules
~~~~~~~~~~~~~~~~~~~~~~

The elimination of ε-rules is performed in a series of consecutive
steps, adding new nonterminals and productions.

As an example grammar we use the one of Figure 4.10 at page 120.

.. code:: ipython3

    G = Grammar.from_string("""
    S -> L a M
    L -> L M 
    L -> ε
    M -> M M
    M -> ε
    """)

Given a rule :math:`A\to ε` we look for rules of the form
:math:`B\to αAβ` and “inline” the ε-rule by adding two new rules
:math:`B\to αA'β` and :math:`B\to αβ` where :math:`A'` is a new
nonterminal; this of course need to be iterated (in a closure) to cope
with productions where :math:`A` appears more than once in the left-hand
side.

.. code:: ipython3

    @closure
    def replace_in_rhs(G, A):
        Ap = A + '’'
        prods = set()
        for B, β in G.P:
            if A in β:
                pos = β.index(A)
                rhs = β[:pos] + β[pos + 1:]
                if len(rhs) == 0: rhs = ('ε', )
                prods.add(Production(B, rhs))
                prods.add(Production(B, β[:pos] + (Ap, ) + β[pos + 1:]))
            else:
                prods.add(Production(B, β))    
        return Grammar(G.N | {Ap}, G.T, prods, G.S)

.. code:: ipython3

    from liblet import prods2table
    
    Gp = replace_in_rhs(G, 'M')
    prods2table(Gp)




.. raw:: html

    <style>td, th {border: 1pt solid lightgray !important ;}</style><table><tr><th><pre>S</pre><td style="text-align:left"><pre>L a | L a M’</pre><tr><th><pre>L</pre><td style="text-align:left"><pre>L | L M’ | ε</pre><tr><th><pre>M</pre><td style="text-align:left"><pre>M’ | M’ M’ | ε</pre><tr><th><pre>M’</pre><td style="text-align:left"><pre></pre></table></table>



The above procedure must be repeated for evey ε-rule, moreover since the
process can intruduce new ε-rules, a closure is again needed.

.. code:: ipython3

    @closure
    def inline_ε_rules(G_seen):
        G, seen = G_seen
        for A in G.N - seen:
            if ('ε', ) in G.alternatives(A):
                return replace_in_rhs(G, A), seen | {A}
        return G, seen

.. code:: ipython3

    Gp, _ = inline_ε_rules((G, set()))
    prods2table(Gp)




.. raw:: html

    <style>td, th {border: 1pt solid lightgray !important ;}</style><table><tr><th><pre>S</pre><td style="text-align:left"><pre>L’ a | L’ a M’ | a | a M’</pre><tr><th><pre>L</pre><td style="text-align:left"><pre>L’ | L’ M’ | M’ | ε</pre><tr><th><pre>L’</pre><td style="text-align:left"><pre></pre><tr><th><pre>M</pre><td style="text-align:left"><pre>M’ | M’ M’ | ε</pre><tr><th><pre>M’</pre><td style="text-align:left"><pre></pre></table></table>



The left-hand sides of the ε rules now are unreachable, but the new
“primed” nonterminals must now be defined, using the non-empty left-hand
sides of the one they inlined.

.. code:: ipython3

    def eliminate_ε_rules(G):
        Gp, _ = inline_ε_rules((G, set()))
        prods = set(Gp.P)
        for Ap in Gp.N - G.N:
            A = Ap[:-1]
            for α in set(Gp.alternatives(A)) - {('ε', )}:
                prods.add(Production(Ap, α))
        return Grammar(Gp.N, Gp.T, prods, Gp.S)

.. code:: ipython3

    prods2table(eliminate_ε_rules(G))




.. raw:: html

    <style>td, th {border: 1pt solid lightgray !important ;}</style><table><tr><th><pre>S</pre><td style="text-align:left"><pre>L’ a | L’ a M’ | a | a M’</pre><tr><th><pre>L</pre><td style="text-align:left"><pre>L’ | L’ M’ | M’ | ε</pre><tr><th><pre>L’</pre><td style="text-align:left"><pre>L’ | L’ M’ | M’</pre><tr><th><pre>M</pre><td style="text-align:left"><pre>M’ | M’ M’ | ε</pre><tr><th><pre>M’</pre><td style="text-align:left"><pre>M’ | M’ M’</pre></table></table>



Removing the unreachable and non-productive rules leads to quite a
drastic simplification!

.. code:: ipython3

    remove_unproductive_unreachable(eliminate_ε_rules(G))




.. parsed-literal::

    Grammar(N={S}, T={a}, P=(S -> a,), S=S)



Elimination of unit rules
~~~~~~~~~~~~~~~~~~~~~~~~~

To see what happens dealing with rules of the form :math:`A\to B` we’ll
refer to a more complex grammar, the one of Figure 4.6 at page 112.

.. code:: ipython3

    G = Grammar.from_string("""
    Number -> Integer | Real
    Integer -> Digit | Integer Digit
    Real -> Integer Fraction Scale
    Fraction -> . Integer
    Scale -> e Sign Integer | Empty
    Digit -> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
    Sign -> + | -
    Empty -> ε
    """)
    prods2table(G)




.. raw:: html

    <style>td, th {border: 1pt solid lightgray !important ;}</style><table><tr><th><pre>Number</pre><td style="text-align:left"><pre>Integer | Real</pre><tr><th><pre>Digit</pre><td style="text-align:left"><pre>0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9</pre><tr><th><pre>Empty</pre><td style="text-align:left"><pre>ε</pre><tr><th><pre>Fraction</pre><td style="text-align:left"><pre>. Integer</pre><tr><th><pre>Integer</pre><td style="text-align:left"><pre>Digit | Integer Digit</pre><tr><th><pre>Real</pre><td style="text-align:left"><pre>Integer Fraction Scale</pre><tr><th><pre>Scale</pre><td style="text-align:left"><pre>Empty | e Sign Integer</pre><tr><th><pre>Sign</pre><td style="text-align:left"><pre>+ | -</pre></table></table>



We start by applying all the cleaning steps seen so far.

.. code:: ipython3

    Gorig = G
    G = remove_unproductive_unreachable(eliminate_ε_rules(G))
    prods2table(G)




.. raw:: html

    <style>td, th {border: 1pt solid lightgray !important ;}</style><table><tr><th><pre>Number</pre><td style="text-align:left"><pre>Integer | Real</pre><tr><th><pre>Digit</pre><td style="text-align:left"><pre>0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9</pre><tr><th><pre>Fraction</pre><td style="text-align:left"><pre>. Integer</pre><tr><th><pre>Integer</pre><td style="text-align:left"><pre>Digit | Integer Digit</pre><tr><th><pre>Real</pre><td style="text-align:left"><pre>Integer Fraction | Integer Fraction Scale’</pre><tr><th><pre>Scale’</pre><td style="text-align:left"><pre>e Sign Integer</pre><tr><th><pre>Sign</pre><td style="text-align:left"><pre>+ | -</pre></table></table>



The elimination of the unit rules is based again on a closure that
replaces :math:`A\to B` and :math:`B\to α` with :math:`A\to α`.

.. code:: ipython3

    def eliminate_unit_rules(G):
        @closure
        def clean(G_seen):
            G, seen = G_seen
            for P in set(filter(Production.such_that(rhs_len = 1), G.P)) - seen:
                A, (B, ) = P
                if B in G.N:            
                    prods = (set(G.P) | {Production(A, α) for α in G.alternatives(B)}) - {P}
                    return Grammar(G.N, G.T, prods, G.S), seen | {P}
            return G, seen
        return clean((G, set()))[0]

.. code:: ipython3

    G = eliminate_unit_rules(G)
    prods2table(G)




.. raw:: html

    <style>td, th {border: 1pt solid lightgray !important ;}</style><table><tr><th><pre>Number</pre><td style="text-align:left"><pre>0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit | Integer Fraction | Integer Fraction Scale’</pre><tr><th><pre>Digit</pre><td style="text-align:left"><pre>0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9</pre><tr><th><pre>Fraction</pre><td style="text-align:left"><pre>. Integer</pre><tr><th><pre>Integer</pre><td style="text-align:left"><pre>0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit</pre><tr><th><pre>Real</pre><td style="text-align:left"><pre>Integer Fraction | Integer Fraction Scale’</pre><tr><th><pre>Scale’</pre><td style="text-align:left"><pre>e Sign Integer</pre><tr><th><pre>Sign</pre><td style="text-align:left"><pre>+ | -</pre></table></table>



The normal form
~~~~~~~~~~~~~~~

Two last cases need to be taken care of to get to the CNF.

First we want to eliminate non-solitary terminals in left-hand sides,
that is if :math:`A\to αaβ` where :math:`a\in T` and
:math:`α, β\in N^*`; this is easily solved by introducing a new
nonterminal :math:`N_a` and a new rule :math:`N_a\to a`, replacing the
offending :math:`A\to αaβ` with :math:`A\to αN_aβ`.

.. code:: ipython3

    def transform_nonsolitary(G):
        prods = set()
        for A, α in G.P:
            if len(α) > 1 and set(α) & G.T:
                rhs = []
                for x in α:
                    if x in G.T:
                        N = 'N{}'.format(x)
                        prods.add(Production(N, (x, )))
                        rhs.append(N)
                    else:
                        rhs.append(x)
                prods.add(Production(A, rhs))
            else:            
                prods.add(Production(A, α))
        return Grammar(G.N | {A for A, α in prods}, G.T, prods, G.S)

.. code:: ipython3

    G = transform_nonsolitary(G)
    prods2table(G)




.. raw:: html

    <style>td, th {border: 1pt solid lightgray !important ;}</style><table><tr><th><pre>Number</pre><td style="text-align:left"><pre>0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit | Integer Fraction | Integer Fraction Scale’</pre><tr><th><pre>Digit</pre><td style="text-align:left"><pre>0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9</pre><tr><th><pre>Fraction</pre><td style="text-align:left"><pre>N. Integer</pre><tr><th><pre>Integer</pre><td style="text-align:left"><pre>0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit</pre><tr><th><pre>N.</pre><td style="text-align:left"><pre>.</pre><tr><th><pre>Ne</pre><td style="text-align:left"><pre>e</pre><tr><th><pre>Real</pre><td style="text-align:left"><pre>Integer Fraction | Integer Fraction Scale’</pre><tr><th><pre>Scale’</pre><td style="text-align:left"><pre>Ne Sign Integer</pre><tr><th><pre>Sign</pre><td style="text-align:left"><pre>+ | -</pre></table></table>



Finally we need to shorten left-hand sides longer than 2 symbols. Again
that is easily accomplished by introducing new nonterminals and rules.

.. code:: ipython3

    def make_binary(G):
        prods = set()
        for A, α in G.P:
            if len(α) > 2:
                Ai = '{}{}'.format(A, 1)
                prods.add(Production(Ai, α[:2]))
                for i, Xi in enumerate(α[2:-1], 2):
                    prods.add(Production('{}{}'.format(A, i), (Ai, Xi)))
                    Ai = '{}{}'.format(A, i)
                prods.add(Production(A, (Ai, α[-1])))
            else:
                prods.add(Production(A, α))
        return Grammar(G.N | {A for A, α in prods}, G.T, prods, G.S)


.. code:: ipython3

    G = make_binary(G)
    prods2table(G)




.. raw:: html

    <style>td, th {border: 1pt solid lightgray !important ;}</style><table><tr><th><pre>Number</pre><td style="text-align:left"><pre>0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit | Integer Fraction | Number1 Scale’</pre><tr><th><pre>Digit</pre><td style="text-align:left"><pre>0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9</pre><tr><th><pre>Fraction</pre><td style="text-align:left"><pre>N. Integer</pre><tr><th><pre>Integer</pre><td style="text-align:left"><pre>0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit</pre><tr><th><pre>N.</pre><td style="text-align:left"><pre>.</pre><tr><th><pre>Ne</pre><td style="text-align:left"><pre>e</pre><tr><th><pre>Number1</pre><td style="text-align:left"><pre>Integer Fraction</pre><tr><th><pre>Real</pre><td style="text-align:left"><pre>Integer Fraction | Real1 Scale’</pre><tr><th><pre>Real1</pre><td style="text-align:left"><pre>Integer Fraction</pre><tr><th><pre>Scale’</pre><td style="text-align:left"><pre>Scale’1 Integer</pre><tr><th><pre>Scale’1</pre><td style="text-align:left"><pre>Ne Sign</pre><tr><th><pre>Sign</pre><td style="text-align:left"><pre>+ | -</pre></table></table>



The Cocke, Younger, and Kasami algorithm
----------------------------------------

Following the CYK description given in Section 4.2.2 of `Parsing
Techniques <https://dickgrune.com//Books/PTAPG_2nd_Edition/>`__ we
implement the algoritm by means of a dictionary ``R`` that, for the key
:math:`(i, l)`, records the left-hand sides of productions deriving
:math:`s_{il}` that is the substring of the input starting at :math:`i`
and having length :math:`l`.

.. code:: ipython3

    def cyk(G, INPUT):
        def fill(R, i, l):
            res = set()
            if l == 1:
                for A, (a,) in filter(Production.such_that(rhs_len = 1), G.P): 
                    if a == INPUT[i - 1]:
                        res.add(A)
            else:
                for k in range(1, l):
                    for A, (B, C) in filter(Production.such_that(rhs_len = 2), G.P):
                        if B in R[(i, k)] and C in R[(i + k, l - k)]:
                            res.add(A)
            return res
        R = {}
        for l in range(1, len(INPUT) + 1):
            for i in range(1, len(INPUT) - l + 2): 
                R[(i, l)] = fill(R, i, l)
        return R

.. code:: ipython3

    from liblet import cyk2table
    
    INPUT = tuple('32.5e+1') # remember: words are sequences of strings!
    R = cyk(G, INPUT)
    cyk2table(R)




.. raw:: html

    <style>td, th {border: 1pt solid lightgray !important ;}</style><table><tr><td style="text-align:left"><pre>Number
    Real</pre></td><tr><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>Number
    Real</pre></td><tr><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><tr><td style="text-align:left"><pre>Number
    Number1
    Real
    Real1</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><tr><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>Number
    Number1
    Real
    Real1</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>Scale’</pre></td><tr><td style="text-align:left"><pre>Integer
    Number</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>Fraction</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>Scale’1</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><tr><td style="text-align:left"><pre>Digit
    Integer
    Number</pre></td><td style="text-align:left"><pre>Digit
    Integer
    Number</pre></td><td style="text-align:left"><pre>N.</pre></td><td style="text-align:left"><pre>Digit
    Integer
    Number</pre></td><td style="text-align:left"><pre>Ne</pre></td><td style="text-align:left"><pre>Sign</pre></td><td style="text-align:left"><pre>Digit
    Integer
    Number</pre></td></table>



Getting the derivation from the table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the table is filled, it’s easy to get a leftmost production by
recursing in the table following the same logic used to fill it.

.. code:: ipython3

    from liblet import show_calls
    
    def get_leftmost_prods(G, R, INPUT):
        @show_calls(True)
        def prods(X, i, l):
            if l == 1:
                return [G.P.index(Production(X, (INPUT[i - 1],)))]
            for A, (B, C) in filter(Production.such_that(lhs = X, rhs_len = 2), G.P):
                for k in range(1, l):
                    if B in R[(i, k)] and C in R[(i + k, l - k)]:
                        return [G.P.index(Production(A, (B, C)))] + prods(B, i, k) + prods(C, i + k, l - k)
        return prods(G.S, 1, len(INPUT))            

.. code:: ipython3

    prods = get_leftmost_prods(G, R, INPUT)


.. parsed-literal::

    ┌prods('Number', 1, 7)
    │┌prods('Number1', 1, 4)
    ││┌prods('Integer', 1, 2)
    │││┌prods('Integer', 1, 1)
    │││└─ [44]
    │││┌prods('Digit', 2, 1)
    │││└─ [23]
    ││└─ [9, 44, 23]
    ││┌prods('Fraction', 3, 2)
    │││┌prods('N.', 3, 1)
    │││└─ [30]
    │││┌prods('Integer', 4, 1)
    │││└─ [34]
    ││└─ [32, 30, 34]
    │└─ [36, 9, 44, 23, 32, 30, 34]
    │┌prods('Scale’', 5, 3)
    ││┌prods('Scale’1', 5, 2)
    │││┌prods('Ne', 5, 1)
    │││└─ [15]
    │││┌prods('Sign', 6, 1)
    │││└─ [38]
    ││└─ [26, 15, 38]
    ││┌prods('Integer', 7, 1)
    ││└─ [12]
    │└─ [22, 26, 15, 38, 12]
    └─ [8, 36, 9, 44, 23, 32, 30, 34, 22, 26, 15, 38, 12]


.. code:: ipython3

    d = Derivation(G)
    for step in prods: d = d.leftmost(step)
    ProductionGraph(d)




.. image:: examples_files/examples_70_0.svg



Undoing the grammar transformation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Following section 4.2.6 of `Parsing
Techniques <https://dickgrune.com//Books/PTAPG_2nd_Edition/>`__, one can
undo the CNF transformation keeping track in ``R`` of symbols that
became useless after the the elimination of ε-rules and unit rules, that
is we clean the original grammar but avoid the
``remove_unproductive_unreachable`` step.

.. code:: ipython3

    Gp = eliminate_unit_rules(eliminate_ε_rules(Gorig))
    Gp = transform_nonsolitary(make_binary(Gp))
    prods2table(Gp)




.. raw:: html

    <style>td, th {border: 1pt solid lightgray !important ;}</style><table><tr><th><pre>Number</pre><td style="text-align:left"><pre>0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit | Integer Fraction | Number1 Scale’</pre><tr><th><pre>Digit</pre><td style="text-align:left"><pre>0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9</pre><tr><th><pre>Empty</pre><td style="text-align:left"><pre>ε</pre><tr><th><pre>Empty’</pre><td style="text-align:left"><pre></pre><tr><th><pre>Fraction</pre><td style="text-align:left"><pre>N. Integer</pre><tr><th><pre>Integer</pre><td style="text-align:left"><pre>0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit</pre><tr><th><pre>N.</pre><td style="text-align:left"><pre>.</pre><tr><th><pre>Ne</pre><td style="text-align:left"><pre>e</pre><tr><th><pre>Number1</pre><td style="text-align:left"><pre>Integer Fraction</pre><tr><th><pre>Real</pre><td style="text-align:left"><pre>Integer Fraction | Real1 Scale’</pre><tr><th><pre>Real1</pre><td style="text-align:left"><pre>Integer Fraction</pre><tr><th><pre>Scale</pre><td style="text-align:left"><pre>Scale1 Integer | ε</pre><tr><th><pre>Scale1</pre><td style="text-align:left"><pre>Ne Sign</pre><tr><th><pre>Scale’</pre><td style="text-align:left"><pre>Scale’1 Integer</pre><tr><th><pre>Scale’1</pre><td style="text-align:left"><pre>Ne Sign</pre><tr><th><pre>Sign</pre><td style="text-align:left"><pre>+ | -</pre></table></table>



We again perform the parsing, this time saving the results in ``Roirg``
table, to which add the end we add a last line with the ε-rules ``Rε``.

.. code:: ipython3

    Rorig = cyk(Gp, INPUT)
    
    Rε = {A for A in Gp.N if ('ε', ) in Gp.alternatives(A)}
    for i in range(1, len(INPUT) + 2): Rorig[(i, 0)] = Rε
        
    cyk2table(Rorig)




.. raw:: html

    <style>td, th {border: 1pt solid lightgray !important ;}</style><table><tr><td style="text-align:left"><pre>Number
    Real</pre></td><tr><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>Number
    Real</pre></td><tr><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><tr><td style="text-align:left"><pre>Number
    Number1
    Real
    Real1</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><tr><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>Number
    Number1
    Real
    Real1</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>Scale
    Scale’</pre></td><tr><td style="text-align:left"><pre>Integer
    Number</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>Fraction</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><td style="text-align:left"><pre>Scale1
    Scale’1</pre></td><td style="text-align:left"><pre>&nbsp;</pre></td><tr><td style="text-align:left"><pre>Digit
    Integer
    Number</pre></td><td style="text-align:left"><pre>Digit
    Integer
    Number</pre></td><td style="text-align:left"><pre>N.</pre></td><td style="text-align:left"><pre>Digit
    Integer
    Number</pre></td><td style="text-align:left"><pre>Ne</pre></td><td style="text-align:left"><pre>Sign</pre></td><td style="text-align:left"><pre>Digit
    Integer
    Number</pre></td><tr><td style="text-align:left"><pre>Empty
    Scale</pre></td><td style="text-align:left"><pre>Empty
    Scale</pre></td><td style="text-align:left"><pre>Empty
    Scale</pre></td><td style="text-align:left"><pre>Empty
    Scale</pre></td><td style="text-align:left"><pre>Empty
    Scale</pre></td><td style="text-align:left"><pre>Empty
    Scale</pre></td><td style="text-align:left"><pre>Empty
    Scale</pre></td><td style="text-align:left"><pre>Empty
    Scale</pre></td></table>



To recover the parse tree, we need a recursive function
``derives(ω, i, l)`` (depending on the grammar and the parse table) that
for a given substring :math:`ω\in (T\cup N)^*` returns a ``lst`` if
:math:`ω` derives the substring :math:`s_{il}`, or ``None`` otherwise,
where ``lst`` is a list :math:`\lambda_0, \lambda_1, \lambda_{l-1}` such
that :math:`\lambda_i` is the length of the substring derived by
:math:`w_i`.

.. code:: ipython3

    def make_derives(R, INPUT):
        def derives(ω, i, l):
            if not ω or ('ε', ) == ω: return [] if l == 0 else None
            X, *χ = ω
            if X in G.T:
                if i <= len(INPUT) and X == INPUT[i - 1]:
                    s = derives(χ, i + 1, l - 1)
                    if s is not None: return [1] + s
            else:
                for k in range(0, l + 1):
                    if X in R[(i, k)]:
                        s = derives(χ, i + k, l - k)
                        if s is not None: return [k] + s
            return None
        return derives

We can for instance test that ``Integer Fraction Scale`` derives
:math:`s_{1,4} =` ``32.5`` as

.. code:: ipython3

    derives = make_derives(Rorig, INPUT)
    derives(['Integer', 'Fraction', 'Scale'], 1, 4)




.. parsed-literal::

    [2, 2, 0]



That tells us that ``Integer`` derives the first 2 input symbols ``32``,
then ``Fraction`` derives the last 2 symbols ``.5`` and finally
``Scale`` derives the empty string.

Endowed with such function, it is easy to adatp ``get_leftmost_prods``
so that it works also for the productions of the original grammar, that
are not in CNF (and can hence have arbitrary length and contain
non-solitary terminals).

.. code:: ipython3

    def get_original_leftmost_prods(G, derives, N):
        @show_calls(True)
        def prods(X, i, l):
            if X in G.T: return []
            for A, α in filter(Production.such_that(lhs = X), G.P):
                d = derives(α, i, l)
                if d is None: continue
                res = [G.P.index(Production(A, α))]
                for B, l in zip(α, d): 
                    res.extend(prods(B, i, l))
                    i += l
                return res
        return prods(G.S, 1, N)

.. code:: ipython3

    prods_orig = get_original_leftmost_prods(Gorig, derives, len(INPUT))
    prods_orig


.. parsed-literal::

    ┌prods('Number', 1, 7)
    │┌prods('Real', 1, 7)
    ││┌prods('Integer', 1, 2)
    │││┌prods('Integer', 1, 1)
    ││││┌prods('Digit', 1, 1)
    │││││┌prods('3', 1, 1)
    │││││└─ []
    ││││└─ [11]
    │││└─ [2, 11]
    │││┌prods('Digit', 2, 1)
    ││││┌prods('2', 2, 1)
    ││││└─ []
    │││└─ [10]
    ││└─ [3, 2, 11, 10]
    ││┌prods('Fraction', 3, 2)
    │││┌prods('.', 3, 1)
    │││└─ []
    │││┌prods('Integer', 4, 1)
    ││││┌prods('Digit', 4, 1)
    │││││┌prods('5', 4, 1)
    │││││└─ []
    ││││└─ [13]
    │││└─ [2, 13]
    ││└─ [5, 2, 13]
    ││┌prods('Scale', 5, 3)
    │││┌prods('e', 5, 1)
    │││└─ []
    │││┌prods('Sign', 6, 1)
    ││││┌prods('+', 6, 1)
    ││││└─ []
    │││└─ [18]
    │││┌prods('Integer', 7, 1)
    ││││┌prods('Digit', 7, 1)
    │││││┌prods('1', 7, 1)
    │││││└─ []
    ││││└─ [9]
    │││└─ [2, 9]
    ││└─ [6, 18, 2, 9]
    │└─ [4, 3, 2, 11, 10, 5, 2, 13, 6, 18, 2, 9]
    └─ [1, 4, 3, 2, 11, 10, 5, 2, 13, 6, 18, 2, 9]




.. parsed-literal::

    [1, 4, 3, 2, 11, 10, 5, 2, 13, 6, 18, 2, 9]



.. code:: ipython3

    d = Derivation(Gorig)
    for step in prods_orig: d = d.leftmost(step)
    ProductionGraph(d)




.. image:: examples_files/examples_82_0.svg


