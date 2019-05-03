
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

    <table class="table-bordered"><tr><th style="text-align:left">0<td style="text-align:left"><pre>S -> a b c</pre>
    <tr><th style="text-align:left">1<td style="text-align:left"><pre>S -> a S Q</pre>
    <tr><th style="text-align:left">2<td style="text-align:left"><pre>b Q c -> b b c c</pre>
    <tr><th style="text-align:left">3<td style="text-align:left"><pre>c Q -> Q c</pre></table>



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

    <table class="table-bordered"><tr><th style="text-align:left">0<td style="text-align:left"><pre>(0, 0)</pre>
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

    <table class="table-bordered"><tr><th style="text-align:left">0<td style="text-align:left"><pre>E -> i</pre>
    <tr><th style="text-align:left">1<td style="text-align:left"><pre>E -> E + E -> i + E -> i + i</pre>
    <tr><th style="text-align:left">2<td style="text-align:left"><pre>E -> E * E -> i * E -> i * i</pre>
    <tr><th style="text-align:left">3<td style="text-align:left"><pre>E -> E + E -> E + E + E -> i + E + E -> i + i + E -> i + i + i</pre>
    <tr><th style="text-align:left">4<td style="text-align:left"><pre>E -> E + E -> E * E + E -> i * E + E -> i * i + E -> i * i + i</pre>
    <tr><th style="text-align:left">5<td style="text-align:left"><pre>E -> E + E -> i + E -> i + E + E -> i + i + E -> i + i + i</pre>
    <tr><th style="text-align:left">6<td style="text-align:left"><pre>E -> E + E -> i + E -> i + E * E -> i + i * E -> i + i * i</pre>
    <tr><th style="text-align:left">7<td style="text-align:left"><pre>E -> E * E -> E + E * E -> i + E * E -> i + i * E -> i + i * i</pre>
    <tr><th style="text-align:left">8<td style="text-align:left"><pre>E -> E * E -> E * E * E -> i * E * E -> i * i * E -> i * i * i</pre>
    <tr><th style="text-align:left">9<td style="text-align:left"><pre>E -> E * E -> i * E -> i * E + E -> i * i + E -> i * i + i</pre></table>



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
    <!-- Generated by graphviz version 2.40.1 (20161225.0304)
     -->
    <!-- Title: %3 Pages: 1 -->
    <svg width="127pt" height="150pt"
     viewBox="0.00 0.00 126.55 150.00" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <g id="graph0" class="graph" transform="scale(1 1) rotate(0) translate(4 146)">
    <title>%3</title>
    <polygon fill="#ffffff" stroke="transparent" points="-4,4 -4,-146 122.5518,-146 122.5518,4 -4,4"/>
    <!-- &#45;1909917890992553030 -->
    <g id="node1" class="node">
    <title>&#45;1909917890992553030</title>
    <path fill="none" stroke="#000000" stroke-width=".25" d="M44.9618,-142C44.9618,-142 39.59,-142 39.59,-142 36.9041,-142 34.2182,-139.3141 34.2182,-136.6282 34.2182,-136.6282 34.2182,-125.3718 34.2182,-125.3718 34.2182,-122.6859 36.9041,-120 39.59,-120 39.59,-120 44.9618,-120 44.9618,-120 47.6477,-120 50.3335,-122.6859 50.3335,-125.3718 50.3335,-125.3718 50.3335,-136.6282 50.3335,-136.6282 50.3335,-139.3141 47.6477,-142 44.9618,-142"/>
    <text text-anchor="middle" x="42.2759" y="-126.8" font-family="Times,serif" font-size="14.00" fill="#000000">E</text>
    </g>
    <!-- &#45;1909919152189551853 -->
    <g id="node2" class="node">
    <title>&#45;1909919152189551853</title>
    <path fill="none" stroke="#000000" stroke-width=".25" d="M10.9618,-102C10.9618,-102 5.59,-102 5.59,-102 2.9041,-102 .2182,-99.3141 .2182,-96.6282 .2182,-96.6282 .2182,-85.3718 .2182,-85.3718 .2182,-82.6859 2.9041,-80 5.59,-80 5.59,-80 10.9618,-80 10.9618,-80 13.6477,-80 16.3335,-82.6859 16.3335,-85.3718 16.3335,-85.3718 16.3335,-96.6282 16.3335,-96.6282 16.3335,-99.3141 13.6477,-102 10.9618,-102"/>
    <text text-anchor="middle" x="8.2759" y="-86.8" font-family="Times,serif" font-size="14.00" fill="#000000">E</text>
    </g>
    <!-- &#45;1909917890992553030&#45;&gt;&#45;1909919152189551853 -->
    <g id="edge1" class="edge">
    <title>&#45;1909917890992553030&#45;&gt;&#45;1909919152189551853</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M34.0454,-121.3171C28.6998,-115.0281 21.761,-106.8649 16.4305,-100.5937"/>
    </g>
    <!-- 9048483434113865714 -->
    <g id="node3" class="node">
    <title>9048483434113865714</title>
    <path fill="none" stroke="#000000" stroke-width="1.25" d="M44.9078,-102C44.9078,-102 39.6439,-102 39.6439,-102 37.012,-102 34.38,-99.3681 34.38,-96.7361 34.38,-96.7361 34.38,-85.2639 34.38,-85.2639 34.38,-82.6319 37.012,-80 39.6439,-80 39.6439,-80 44.9078,-80 44.9078,-80 47.5398,-80 50.1717,-82.6319 50.1717,-85.2639 50.1717,-85.2639 50.1717,-96.7361 50.1717,-96.7361 50.1717,-99.3681 47.5398,-102 44.9078,-102"/>
    <text text-anchor="middle" x="42.2759" y="-86.8" font-family="Times,serif" font-size="14.00" fill="#000000">+</text>
    </g>
    <!-- &#45;1909917890992553030&#45;&gt;9048483434113865714 -->
    <g id="edge2" class="edge">
    <title>&#45;1909917890992553030&#45;&gt;9048483434113865714</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M42.2759,-119.6446C42.2759,-114.1937 42.2759,-107.6819 42.2759,-102.2453"/>
    </g>
    <!-- &#45;1909919152187221755 -->
    <g id="node4" class="node">
    <title>&#45;1909919152187221755</title>
    <path fill="none" stroke="#000000" stroke-width=".25" d="M78.9618,-102C78.9618,-102 73.59,-102 73.59,-102 70.9041,-102 68.2182,-99.3141 68.2182,-96.6282 68.2182,-96.6282 68.2182,-85.3718 68.2182,-85.3718 68.2182,-82.6859 70.9041,-80 73.59,-80 73.59,-80 78.9618,-80 78.9618,-80 81.6477,-80 84.3335,-82.6859 84.3335,-85.3718 84.3335,-85.3718 84.3335,-96.6282 84.3335,-96.6282 84.3335,-99.3141 81.6477,-102 78.9618,-102"/>
    <text text-anchor="middle" x="76.2759" y="-86.8" font-family="Times,serif" font-size="14.00" fill="#000000">E</text>
    </g>
    <!-- &#45;1909917890992553030&#45;&gt;&#45;1909919152187221755 -->
    <g id="edge3" class="edge">
    <title>&#45;1909917890992553030&#45;&gt;&#45;1909919152187221755</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M50.5063,-121.3171C55.852,-115.0281 62.7907,-106.8649 68.1212,-100.5937"/>
    </g>
    <!-- &#45;1909919152189551853&#45;&gt;9048483434113865714 -->
    <!-- 1647678174847162503 -->
    <g id="node5" class="node">
    <title>1647678174847162503</title>
    <path fill="none" stroke="#000000" stroke-width="1.25" d="M10.2393,-62C10.2393,-62 6.3125,-62 6.3125,-62 4.3491,-62 2.3857,-60.0366 2.3857,-58.0732 2.3857,-58.0732 2.3857,-43.9268 2.3857,-43.9268 2.3857,-41.9634 4.3491,-40 6.3125,-40 6.3125,-40 10.2393,-40 10.2393,-40 12.2026,-40 14.166,-41.9634 14.166,-43.9268 14.166,-43.9268 14.166,-58.0732 14.166,-58.0732 14.166,-60.0366 12.2026,-62 10.2393,-62"/>
    <text text-anchor="middle" x="8.2759" y="-46.8" font-family="Times,serif" font-size="14.00" fill="#000000">i</text>
    </g>
    <!-- &#45;1909919152189551853&#45;&gt;1647678174847162503 -->
    <g id="edge6" class="edge">
    <title>&#45;1909919152189551853&#45;&gt;1647678174847162503</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M8.2759,-79.6446C8.2759,-74.1937 8.2759,-67.6819 8.2759,-62.2453"/>
    </g>
    <!-- 9048483434113865714&#45;&gt;&#45;1909919152187221755 -->
    <!-- &#45;1909916629795554207 -->
    <g id="node6" class="node">
    <title>&#45;1909916629795554207</title>
    <path fill="none" stroke="#000000" stroke-width=".25" d="M44.9618,-62C44.9618,-62 39.59,-62 39.59,-62 36.9041,-62 34.2182,-59.3141 34.2182,-56.6282 34.2182,-56.6282 34.2182,-45.3718 34.2182,-45.3718 34.2182,-42.6859 36.9041,-40 39.59,-40 39.59,-40 44.9618,-40 44.9618,-40 47.6477,-40 50.3335,-42.6859 50.3335,-45.3718 50.3335,-45.3718 50.3335,-56.6282 50.3335,-56.6282 50.3335,-59.3141 47.6477,-62 44.9618,-62"/>
    <text text-anchor="middle" x="42.2759" y="-46.8" font-family="Times,serif" font-size="14.00" fill="#000000">E</text>
    </g>
    <!-- &#45;1909919152187221755&#45;&gt;&#45;1909916629795554207 -->
    <g id="edge7" class="edge">
    <title>&#45;1909919152187221755&#45;&gt;&#45;1909916629795554207</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M68.0454,-81.3171C62.6998,-75.0281 55.761,-66.8649 50.4305,-60.5937"/>
    </g>
    <!-- 1223704543038443683 -->
    <g id="node7" class="node">
    <title>1223704543038443683</title>
    <path fill="none" stroke="#000000" stroke-width="1.25" d="M78.7759,-62C78.7759,-62 73.7759,-62 73.7759,-62 71.2759,-62 68.7759,-59.5 68.7759,-57 68.7759,-57 68.7759,-45 68.7759,-45 68.7759,-42.5 71.2759,-40 73.7759,-40 73.7759,-40 78.7759,-40 78.7759,-40 81.2759,-40 83.7759,-42.5 83.7759,-45 83.7759,-45 83.7759,-57 83.7759,-57 83.7759,-59.5 81.2759,-62 78.7759,-62"/>
    <text text-anchor="middle" x="76.2759" y="-46.8" font-family="Times,serif" font-size="14.00" fill="#000000">*</text>
    </g>
    <!-- &#45;1909919152187221755&#45;&gt;1223704543038443683 -->
    <g id="edge8" class="edge">
    <title>&#45;1909919152187221755&#45;&gt;1223704543038443683</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M76.2759,-79.6446C76.2759,-74.1937 76.2759,-67.6819 76.2759,-62.2453"/>
    </g>
    <!-- &#45;1909916629797884305 -->
    <g id="node8" class="node">
    <title>&#45;1909916629797884305</title>
    <path fill="none" stroke="#000000" stroke-width=".25" d="M112.9618,-62C112.9618,-62 107.59,-62 107.59,-62 104.9041,-62 102.2182,-59.3141 102.2182,-56.6282 102.2182,-56.6282 102.2182,-45.3718 102.2182,-45.3718 102.2182,-42.6859 104.9041,-40 107.59,-40 107.59,-40 112.9618,-40 112.9618,-40 115.6477,-40 118.3335,-42.6859 118.3335,-45.3718 118.3335,-45.3718 118.3335,-56.6282 118.3335,-56.6282 118.3335,-59.3141 115.6477,-62 112.9618,-62"/>
    <text text-anchor="middle" x="110.2759" y="-46.8" font-family="Times,serif" font-size="14.00" fill="#000000">E</text>
    </g>
    <!-- &#45;1909919152187221755&#45;&gt;&#45;1909916629797884305 -->
    <g id="edge9" class="edge">
    <title>&#45;1909919152187221755&#45;&gt;&#45;1909916629797884305</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M84.5063,-81.3171C89.852,-75.0281 96.7907,-66.8649 102.1212,-60.5937"/>
    </g>
    <!-- &#45;1909916629795554207&#45;&gt;1223704543038443683 -->
    <!-- 1647675652453164857 -->
    <g id="node9" class="node">
    <title>1647675652453164857</title>
    <path fill="none" stroke="#000000" stroke-width="1.25" d="M44.2393,-22C44.2393,-22 40.3125,-22 40.3125,-22 38.3491,-22 36.3857,-20.0366 36.3857,-18.0732 36.3857,-18.0732 36.3857,-3.9268 36.3857,-3.9268 36.3857,-1.9634 38.3491,0 40.3125,0 40.3125,0 44.2393,0 44.2393,0 46.2026,0 48.166,-1.9634 48.166,-3.9268 48.166,-3.9268 48.166,-18.0732 48.166,-18.0732 48.166,-20.0366 46.2026,-22 44.2393,-22"/>
    <text text-anchor="middle" x="42.2759" y="-6.8" font-family="Times,serif" font-size="14.00" fill="#000000">i</text>
    </g>
    <!-- &#45;1909916629795554207&#45;&gt;1647675652453164857 -->
    <g id="edge12" class="edge">
    <title>&#45;1909916629795554207&#45;&gt;1647675652453164857</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M42.2759,-39.6446C42.2759,-34.1937 42.2759,-27.6819 42.2759,-22.2453"/>
    </g>
    <!-- 1223704543038443683&#45;&gt;&#45;1909916629797884305 -->
    <!-- 1647676913650163680 -->
    <g id="node10" class="node">
    <title>1647676913650163680</title>
    <path fill="none" stroke="#000000" stroke-width="1.25" d="M112.2393,-22C112.2393,-22 108.3125,-22 108.3125,-22 106.3491,-22 104.3857,-20.0366 104.3857,-18.0732 104.3857,-18.0732 104.3857,-3.9268 104.3857,-3.9268 104.3857,-1.9634 106.3491,0 108.3125,0 108.3125,0 112.2393,0 112.2393,0 114.2026,0 116.166,-1.9634 116.166,-3.9268 116.166,-3.9268 116.166,-18.0732 116.166,-18.0732 116.166,-20.0366 114.2026,-22 112.2393,-22"/>
    <text text-anchor="middle" x="110.2759" y="-6.8" font-family="Times,serif" font-size="14.00" fill="#000000">i</text>
    </g>
    <!-- &#45;1909916629797884305&#45;&gt;1647676913650163680 -->
    <g id="edge13" class="edge">
    <title>&#45;1909916629797884305&#45;&gt;1647676913650163680</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M110.2759,-39.6446C110.2759,-34.1937 110.2759,-27.6819 110.2759,-22.2453"/>
    </g>
    </g>
    </svg>
     <?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
     "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <!-- Generated by graphviz version 2.40.1 (20161225.0304)
     -->
    <!-- Title: %3 Pages: 1 -->
    <svg width="127pt" height="150pt"
     viewBox="0.00 0.00 126.55 150.00" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <g id="graph0" class="graph" transform="scale(1 1) rotate(0) translate(4 146)">
    <title>%3</title>
    <polygon fill="#ffffff" stroke="transparent" points="-4,4 -4,-146 122.5518,-146 122.5518,4 -4,4"/>
    <!-- &#45;1909917890992553030 -->
    <g id="node1" class="node">
    <title>&#45;1909917890992553030</title>
    <path fill="none" stroke="#000000" stroke-width=".25" d="M78.9618,-142C78.9618,-142 73.59,-142 73.59,-142 70.9041,-142 68.2182,-139.3141 68.2182,-136.6282 68.2182,-136.6282 68.2182,-125.3718 68.2182,-125.3718 68.2182,-122.6859 70.9041,-120 73.59,-120 73.59,-120 78.9618,-120 78.9618,-120 81.6477,-120 84.3335,-122.6859 84.3335,-125.3718 84.3335,-125.3718 84.3335,-136.6282 84.3335,-136.6282 84.3335,-139.3141 81.6477,-142 78.9618,-142"/>
    <text text-anchor="middle" x="76.2759" y="-126.8" font-family="Times,serif" font-size="14.00" fill="#000000">E</text>
    </g>
    <!-- &#45;1909919152189551853 -->
    <g id="node2" class="node">
    <title>&#45;1909919152189551853</title>
    <path fill="none" stroke="#000000" stroke-width=".25" d="M44.9618,-102C44.9618,-102 39.59,-102 39.59,-102 36.9041,-102 34.2182,-99.3141 34.2182,-96.6282 34.2182,-96.6282 34.2182,-85.3718 34.2182,-85.3718 34.2182,-82.6859 36.9041,-80 39.59,-80 39.59,-80 44.9618,-80 44.9618,-80 47.6477,-80 50.3335,-82.6859 50.3335,-85.3718 50.3335,-85.3718 50.3335,-96.6282 50.3335,-96.6282 50.3335,-99.3141 47.6477,-102 44.9618,-102"/>
    <text text-anchor="middle" x="42.2759" y="-86.8" font-family="Times,serif" font-size="14.00" fill="#000000">E</text>
    </g>
    <!-- &#45;1909917890992553030&#45;&gt;&#45;1909919152189551853 -->
    <g id="edge1" class="edge">
    <title>&#45;1909917890992553030&#45;&gt;&#45;1909919152189551853</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M68.0454,-121.3171C62.6998,-115.0281 55.761,-106.8649 50.4305,-100.5937"/>
    </g>
    <!-- 1223702020644446037 -->
    <g id="node3" class="node">
    <title>1223702020644446037</title>
    <path fill="none" stroke="#000000" stroke-width="1.25" d="M78.7759,-102C78.7759,-102 73.7759,-102 73.7759,-102 71.2759,-102 68.7759,-99.5 68.7759,-97 68.7759,-97 68.7759,-85 68.7759,-85 68.7759,-82.5 71.2759,-80 73.7759,-80 73.7759,-80 78.7759,-80 78.7759,-80 81.2759,-80 83.7759,-82.5 83.7759,-85 83.7759,-85 83.7759,-97 83.7759,-97 83.7759,-99.5 81.2759,-102 78.7759,-102"/>
    <text text-anchor="middle" x="76.2759" y="-86.8" font-family="Times,serif" font-size="14.00" fill="#000000">*</text>
    </g>
    <!-- &#45;1909917890992553030&#45;&gt;1223702020644446037 -->
    <g id="edge2" class="edge">
    <title>&#45;1909917890992553030&#45;&gt;1223702020644446037</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M76.2759,-119.6446C76.2759,-114.1937 76.2759,-107.6819 76.2759,-102.2453"/>
    </g>
    <!-- &#45;1909919152187221755 -->
    <g id="node4" class="node">
    <title>&#45;1909919152187221755</title>
    <path fill="none" stroke="#000000" stroke-width=".25" d="M112.9618,-102C112.9618,-102 107.59,-102 107.59,-102 104.9041,-102 102.2182,-99.3141 102.2182,-96.6282 102.2182,-96.6282 102.2182,-85.3718 102.2182,-85.3718 102.2182,-82.6859 104.9041,-80 107.59,-80 107.59,-80 112.9618,-80 112.9618,-80 115.6477,-80 118.3335,-82.6859 118.3335,-85.3718 118.3335,-85.3718 118.3335,-96.6282 118.3335,-96.6282 118.3335,-99.3141 115.6477,-102 112.9618,-102"/>
    <text text-anchor="middle" x="110.2759" y="-86.8" font-family="Times,serif" font-size="14.00" fill="#000000">E</text>
    </g>
    <!-- &#45;1909917890992553030&#45;&gt;&#45;1909919152187221755 -->
    <g id="edge3" class="edge">
    <title>&#45;1909917890992553030&#45;&gt;&#45;1909919152187221755</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M84.5063,-121.3171C89.852,-115.0281 96.7907,-106.8649 102.1212,-100.5937"/>
    </g>
    <!-- &#45;1909919152189551853&#45;&gt;1223702020644446037 -->
    <!-- &#45;1909915368598555384 -->
    <g id="node5" class="node">
    <title>&#45;1909915368598555384</title>
    <path fill="none" stroke="#000000" stroke-width=".25" d="M10.9618,-62C10.9618,-62 5.59,-62 5.59,-62 2.9041,-62 .2182,-59.3141 .2182,-56.6282 .2182,-56.6282 .2182,-45.3718 .2182,-45.3718 .2182,-42.6859 2.9041,-40 5.59,-40 5.59,-40 10.9618,-40 10.9618,-40 13.6477,-40 16.3335,-42.6859 16.3335,-45.3718 16.3335,-45.3718 16.3335,-56.6282 16.3335,-56.6282 16.3335,-59.3141 13.6477,-62 10.9618,-62"/>
    <text text-anchor="middle" x="8.2759" y="-46.8" font-family="Times,serif" font-size="14.00" fill="#000000">E</text>
    </g>
    <!-- &#45;1909919152189551853&#45;&gt;&#45;1909915368598555384 -->
    <g id="edge6" class="edge">
    <title>&#45;1909919152189551853&#45;&gt;&#45;1909915368598555384</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M34.0454,-81.3171C28.6998,-75.0281 21.761,-66.8649 16.4305,-60.5937"/>
    </g>
    <!-- 9048482172914536793 -->
    <g id="node6" class="node">
    <title>9048482172914536793</title>
    <path fill="none" stroke="#000000" stroke-width="1.25" d="M44.9078,-62C44.9078,-62 39.6439,-62 39.6439,-62 37.012,-62 34.38,-59.3681 34.38,-56.7361 34.38,-56.7361 34.38,-45.2639 34.38,-45.2639 34.38,-42.6319 37.012,-40 39.6439,-40 39.6439,-40 44.9078,-40 44.9078,-40 47.5398,-40 50.1717,-42.6319 50.1717,-45.2639 50.1717,-45.2639 50.1717,-56.7361 50.1717,-56.7361 50.1717,-59.3681 47.5398,-62 44.9078,-62"/>
    <text text-anchor="middle" x="42.2759" y="-46.8" font-family="Times,serif" font-size="14.00" fill="#000000">+</text>
    </g>
    <!-- &#45;1909919152189551853&#45;&gt;9048482172914536793 -->
    <g id="edge7" class="edge">
    <title>&#45;1909919152189551853&#45;&gt;9048482172914536793</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M42.2759,-79.6446C42.2759,-74.1937 42.2759,-67.6819 42.2759,-62.2453"/>
    </g>
    <!-- &#45;1909915368596225286 -->
    <g id="node7" class="node">
    <title>&#45;1909915368596225286</title>
    <path fill="none" stroke="#000000" stroke-width=".25" d="M78.9618,-62C78.9618,-62 73.59,-62 73.59,-62 70.9041,-62 68.2182,-59.3141 68.2182,-56.6282 68.2182,-56.6282 68.2182,-45.3718 68.2182,-45.3718 68.2182,-42.6859 70.9041,-40 73.59,-40 73.59,-40 78.9618,-40 78.9618,-40 81.6477,-40 84.3335,-42.6859 84.3335,-45.3718 84.3335,-45.3718 84.3335,-56.6282 84.3335,-56.6282 84.3335,-59.3141 81.6477,-62 78.9618,-62"/>
    <text text-anchor="middle" x="76.2759" y="-46.8" font-family="Times,serif" font-size="14.00" fill="#000000">E</text>
    </g>
    <!-- &#45;1909919152189551853&#45;&gt;&#45;1909915368596225286 -->
    <g id="edge8" class="edge">
    <title>&#45;1909919152189551853&#45;&gt;&#45;1909915368596225286</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M50.5063,-81.3171C55.852,-75.0281 62.7907,-66.8649 68.1212,-60.5937"/>
    </g>
    <!-- 1223702020644446037&#45;&gt;&#45;1909919152187221755 -->
    <!-- 1647676913650163680 -->
    <g id="node10" class="node">
    <title>1647676913650163680</title>
    <path fill="none" stroke="#000000" stroke-width="1.25" d="M112.2393,-62C112.2393,-62 108.3125,-62 108.3125,-62 106.3491,-62 104.3857,-60.0366 104.3857,-58.0732 104.3857,-58.0732 104.3857,-43.9268 104.3857,-43.9268 104.3857,-41.9634 106.3491,-40 108.3125,-40 108.3125,-40 112.2393,-40 112.2393,-40 114.2026,-40 116.166,-41.9634 116.166,-43.9268 116.166,-43.9268 116.166,-58.0732 116.166,-58.0732 116.166,-60.0366 114.2026,-62 112.2393,-62"/>
    <text text-anchor="middle" x="110.2759" y="-46.8" font-family="Times,serif" font-size="14.00" fill="#000000">i</text>
    </g>
    <!-- &#45;1909919152187221755&#45;&gt;1647676913650163680 -->
    <g id="edge13" class="edge">
    <title>&#45;1909919152187221755&#45;&gt;1647676913650163680</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M110.2759,-79.6446C110.2759,-74.1937 110.2759,-67.6819 110.2759,-62.2453"/>
    </g>
    <!-- &#45;1909915368598555384&#45;&gt;9048482172914536793 -->
    <!-- 1647679436044161326 -->
    <g id="node8" class="node">
    <title>1647679436044161326</title>
    <path fill="none" stroke="#000000" stroke-width="1.25" d="M10.2393,-22C10.2393,-22 6.3125,-22 6.3125,-22 4.3491,-22 2.3857,-20.0366 2.3857,-18.0732 2.3857,-18.0732 2.3857,-3.9268 2.3857,-3.9268 2.3857,-1.9634 4.3491,0 6.3125,0 6.3125,0 10.2393,0 10.2393,0 12.2026,0 14.166,-1.9634 14.166,-3.9268 14.166,-3.9268 14.166,-18.0732 14.166,-18.0732 14.166,-20.0366 12.2026,-22 10.2393,-22"/>
    <text text-anchor="middle" x="8.2759" y="-6.8" font-family="Times,serif" font-size="14.00" fill="#000000">i</text>
    </g>
    <!-- &#45;1909915368598555384&#45;&gt;1647679436044161326 -->
    <g id="edge11" class="edge">
    <title>&#45;1909915368598555384&#45;&gt;1647679436044161326</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M8.2759,-39.6446C8.2759,-34.1937 8.2759,-27.6819 8.2759,-22.2453"/>
    </g>
    <!-- 9048482172914536793&#45;&gt;&#45;1909915368596225286 -->
    <!-- 1647675652453164857 -->
    <g id="node9" class="node">
    <title>1647675652453164857</title>
    <path fill="none" stroke="#000000" stroke-width="1.25" d="M78.2393,-22C78.2393,-22 74.3125,-22 74.3125,-22 72.3491,-22 70.3857,-20.0366 70.3857,-18.0732 70.3857,-18.0732 70.3857,-3.9268 70.3857,-3.9268 70.3857,-1.9634 72.3491,0 74.3125,0 74.3125,0 78.2393,0 78.2393,0 80.2026,0 82.166,-1.9634 82.166,-3.9268 82.166,-3.9268 82.166,-18.0732 82.166,-18.0732 82.166,-20.0366 80.2026,-22 78.2393,-22"/>
    <text text-anchor="middle" x="76.2759" y="-6.8" font-family="Times,serif" font-size="14.00" fill="#000000">i</text>
    </g>
    <!-- &#45;1909915368596225286&#45;&gt;1647675652453164857 -->
    <g id="edge12" class="edge">
    <title>&#45;1909915368596225286&#45;&gt;1647675652453164857</title>
    <path fill="none" stroke="#000000" stroke-width=".5" d="M76.2759,-39.6446C76.2759,-34.1937 76.2759,-27.6819 76.2759,-22.2453"/>
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
left-hand sides of productions whose left-hand sides are in turn made
of productive symbols.

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
union all the left-hand sides of productions whose left-hand sides
are in turn reachable.

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
with productions where :math:`A` appears more than once in the
left-hand side.

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

    <table class="table-bordered"><tr><th>S<td style="text-align:left">L a | L a M’<tr><th>L<td style="text-align:left">L | L M’ | ε<tr><th>M<td style="text-align:left">M’ | M’ M’ | ε<tr><th>M’<td style="text-align:left"></table>



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

    <table class="table-bordered"><tr><th>S<td style="text-align:left">L’ a | L’ a M’ | a | a M’<tr><th>L<td style="text-align:left">L’ | L’ M’ | M’ | ε<tr><th>L’<td style="text-align:left"><tr><th>M<td style="text-align:left">M’ | M’ M’ | ε<tr><th>M’<td style="text-align:left"></table>



The left-hand sides of the ε rules now are unreachable, but the new
“primed” nonterminals must now be defined, using the non-empty
left-hand sides of the one they inlined.

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

    <table class="table-bordered"><tr><th>S<td style="text-align:left">L’ a | L’ a M’ | a | a M’<tr><th>L<td style="text-align:left">L’ | L’ M’ | M’ | ε<tr><th>L’<td style="text-align:left">L’ | L’ M’ | M’<tr><th>M<td style="text-align:left">M’ | M’ M’ | ε<tr><th>M’<td style="text-align:left">M’ | M’ M’</table>



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

    <table class="table-bordered"><tr><th>Number<td style="text-align:left">Integer | Real<tr><th>Digit<td style="text-align:left">0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9<tr><th>Empty<td style="text-align:left">ε<tr><th>Fraction<td style="text-align:left">. Integer<tr><th>Integer<td style="text-align:left">Digit | Integer Digit<tr><th>Real<td style="text-align:left">Integer Fraction Scale<tr><th>Scale<td style="text-align:left">Empty | e Sign Integer<tr><th>Sign<td style="text-align:left">+ | -</table>



We start by applying all the cleaning steps seen so far.

.. code:: ipython3

    Gorig = G
    G = remove_unproductive_unreachable(eliminate_ε_rules(G))
    prods2table(G)




.. raw:: html

    <table class="table-bordered"><tr><th>Number<td style="text-align:left">Integer | Real<tr><th>Digit<td style="text-align:left">0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9<tr><th>Fraction<td style="text-align:left">. Integer<tr><th>Integer<td style="text-align:left">Digit | Integer Digit<tr><th>Real<td style="text-align:left">Integer Fraction | Integer Fraction Scale’<tr><th>Scale’<td style="text-align:left">e Sign Integer<tr><th>Sign<td style="text-align:left">+ | -</table>



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

    <table class="table-bordered"><tr><th>Number<td style="text-align:left">0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit | Integer Fraction | Integer Fraction Scale’<tr><th>Digit<td style="text-align:left">0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9<tr><th>Fraction<td style="text-align:left">. Integer<tr><th>Integer<td style="text-align:left">0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit<tr><th>Real<td style="text-align:left">Integer Fraction | Integer Fraction Scale’<tr><th>Scale’<td style="text-align:left">e Sign Integer<tr><th>Sign<td style="text-align:left">+ | -</table>



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

    <table class="table-bordered"><tr><th>Number<td style="text-align:left">0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit | Integer Fraction | Integer Fraction Scale’<tr><th>Digit<td style="text-align:left">0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9<tr><th>Fraction<td style="text-align:left">N. Integer<tr><th>Integer<td style="text-align:left">0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit<tr><th>N.<td style="text-align:left">.<tr><th>Ne<td style="text-align:left">e<tr><th>Real<td style="text-align:left">Integer Fraction | Integer Fraction Scale’<tr><th>Scale’<td style="text-align:left">Ne Sign Integer<tr><th>Sign<td style="text-align:left">+ | -</table>



Finally we need to shorten left-hand sides longer than 2 symbols.
Again that is easily accomplished by introducing new nonterminals and
rules.

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

    <table class="table-bordered"><tr><th>Number<td style="text-align:left">0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit | Integer Fraction | Number1 Scale’<tr><th>Digit<td style="text-align:left">0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9<tr><th>Fraction<td style="text-align:left">N. Integer<tr><th>Integer<td style="text-align:left">0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit<tr><th>N.<td style="text-align:left">.<tr><th>Ne<td style="text-align:left">e<tr><th>Number1<td style="text-align:left">Integer Fraction<tr><th>Real<td style="text-align:left">Integer Fraction | Real1 Scale’<tr><th>Real1<td style="text-align:left">Integer Fraction<tr><th>Scale’<td style="text-align:left">Scale’1 Integer<tr><th>Scale’1<td style="text-align:left">Ne Sign<tr><th>Sign<td style="text-align:left">+ | -</table>



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
    
    INPUT = '32.5e+1'
    R = cyk(G, INPUT)
    cyk2table(R)




.. raw:: html

    <table class="table-bordered"><tr><td style="text-align:left"><pre>Number
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
    │││└─ [25]
    │││┌prods('Digit', 2, 1)
    │││└─ [40]
    ││└─ [28, 25, 40]
    ││┌prods('Fraction', 3, 2)
    │││┌prods('N.', 3, 1)
    │││└─ [18]
    │││┌prods('Integer', 4, 1)
    │││└─ [35]
    ││└─ [15, 18, 35]
    │└─ [14, 28, 25, 40, 15, 18, 35]
    │┌prods('Scale’', 5, 3)
    ││┌prods('Scale’1', 5, 2)
    │││┌prods('Ne', 5, 1)
    │││└─ [37]
    │││┌prods('Sign', 6, 1)
    │││└─ [9]
    ││└─ [42, 37, 9]
    ││┌prods('Integer', 7, 1)
    ││└─ [19]
    │└─ [24, 42, 37, 9, 19]
    └─ [38, 14, 28, 25, 40, 15, 18, 35, 24, 42, 37, 9, 19]


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

    <table class="table-bordered"><tr><th>Number<td style="text-align:left">0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit | Integer Fraction | Number1 Scale’<tr><th>Digit<td style="text-align:left">0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9<tr><th>Empty<td style="text-align:left">ε<tr><th>Empty’<td style="text-align:left"><tr><th>Fraction<td style="text-align:left">N. Integer<tr><th>Integer<td style="text-align:left">0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Integer Digit<tr><th>N.<td style="text-align:left">.<tr><th>Ne<td style="text-align:left">e<tr><th>Number1<td style="text-align:left">Integer Fraction<tr><th>Real<td style="text-align:left">Integer Fraction | Real1 Scale’<tr><th>Real1<td style="text-align:left">Integer Fraction<tr><th>Scale<td style="text-align:left">Scale1 Integer | ε<tr><th>Scale1<td style="text-align:left">Ne Sign<tr><th>Scale’<td style="text-align:left">Scale’1 Integer<tr><th>Scale’1<td style="text-align:left">Ne Sign<tr><th>Sign<td style="text-align:left">+ | -</table>



We again perform the parsing, this time saving the results in ``Roirg``
table, to which add the end we add a last line with the ε-rules ``Rε``.

.. code:: ipython3

    Rorig = cyk(Gp, INPUT)
    
    Rε = {A for A in Gp.N if ('ε', ) in Gp.alternatives(A)}
    for i in range(1, len(INPUT) + 2): Rorig[(i, 0)] = Rε
        
    cyk2table(Rorig)




.. raw:: html

    <table class="table-bordered"><tr><td style="text-align:left"><pre>Number
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
for a given substring :math:`ω\in (T\cup N)^*` returns a ``True, lst``
if :math:`ω` derives the substring :math:`s_{il}` and ``lst`` is a list
:math:`\lambda_0, \lambda_1, \lambda_{l-1}` such that :math:`\lambda_i`
is the length of the substring derived by :math:`w_i`.

.. code:: ipython3

    def make_derives(R, INPUT):
        def derives(ω, i, l):
            if not ω or ('ε', ) == ω: return l == 0, []
            X, *χ = ω
            if X in G.T:
                if i <= len(INPUT) and X == INPUT[i - 1]:
                    d, s = derives(χ, i + 1, l - 1)
                    if d: return True, [1] + s
            else:
                for k in range(0, l + 1):
                    if X in R[(i, k)]:
                        d, s = derives(χ, i + k, l - k)
                        if d: return True, [k] + s
            return False, []
        return derives

We can for instance test that ``Integer Fraction Scale`` derives
:math:`s_{1,4} =` ``32.5`` as

.. code:: ipython3

    derives = make_derives(Rorig, INPUT)
    derives(['Integer', 'Fraction', 'Scale'], 1, 4)




.. parsed-literal::

    (True, [2, 2, 0])



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
                d, sp = derives(α, i, l)
                if not d: continue
                res = [G.P.index(Production(A, α))]
                for B, l in zip(α, sp): 
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


