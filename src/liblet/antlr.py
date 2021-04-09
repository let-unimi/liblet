from contextlib import redirect_stderr
from importlib import util as imputil
from io import StringIO
from os import environ
from os.path import join as pjoin, exists
from re import findall
from subprocess import run
from sys import modules
from tempfile import TemporaryDirectory
from textwrap import indent

from antlr4.atn.PredictionMode import PredictionMode
from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.error.DiagnosticErrorListener import DiagnosticErrorListener
from antlr4.InputStream import InputStream
from antlr4.tree.Tree import ParseTreeVisitor

from .display import Tree
from .utils import warn

if not 'READTHEDOCS' in environ: # pragma: nocover
    if 'ANTLR4_JAR' not in environ:
        raise ImportError('Please define the ANTLR4_JAR environment variable')
    if not exists(environ['ANTLR4_JAR']):
        raise ImportError('The ANTLR4_JAR environment variable points to "{}" that is not an existing file'.format(environ['ANTLR4_JAR']))

# Consider refactoring in .parse_tree returning antlr context object and .tree returning a Tree

class ANTLR:
    """An utility class representing an ANTLR (v4) grammar and code generated from it.

    Given the *grammar* the constructor of this class **generates the code** for the
    *lexer*, *parser*, *visitor*, and *listener* using the ANTLR tool; if no errors
    are found, it then **loads the modules** (with their original names) and stores
    a reference to them in the attributes named :attr:`Lexer`, :attr:`Parser`, :attr:`Visitor`, and
    :attr:`Listener`. If the constructor is called a second time, it correctly *unloads
    the previously generated modules* (so that the current one are correctly
    corresponding to the current grammar). Moreover, to facilitate *debugging the
    grammar* it keeps track both of the grammar source (in an attribute of the same name)
    and of the sources of the generated modules, in an attribute named :attr:`source` that
    is a :obj:`dict` indexed by ``Lexer``, ``Parser``, ``Visitor``, and ``Listener``.

    Args:
        grammar (str): the grammar to process (in ANTLR v4 format).

    Raises:
        ValueError: if the grammar does not contain the name.
    """
    __slots__ = ('name', 'Lexer', 'Parser', 'Visitor', 'Listener', 'source', 'grammar')

    def __init__(self, grammar):

        self.grammar = grammar
        try:
            name = findall(r'grammar\s+(\w+)\s*;', grammar)[0]
        except IndexError:
            raise ValueError('Grammar name not found')
        self.name = name
        self.source = {}

        with TemporaryDirectory() as tmpdir:

            with open(pjoin(tmpdir, name) + '.g', 'w') as ouf: ouf.write(grammar)
            res = run([
                'java', '-jar', environ['ANTLR4_JAR'],
                '-Dlanguage=Python3',
                '-listener', '-visitor',
                '{}.g'.format(name)
            ], capture_output = True, cwd = tmpdir)
            if res.returncode:
                warn(res.stderr.decode('utf-8'))
                return

            for suffix in  'Lexer', 'Parser', 'Visitor', 'Listener': # the order is crucial, due to the module loading/execution sequence
                qn = '{}{}'.format(name, suffix)
                if qn in modules: del modules[qn]
                src_path = pjoin(tmpdir, qn) + '.py'
                with open(src_path, 'r') as inf: self.source[suffix] = inf.read()
                spec = imputil.spec_from_file_location(qn, src_path)
                module = imputil.module_from_spec(spec)
                spec.loader.exec_module(module)
                modules[qn] = module
                setattr(self, suffix, getattr(module, qn))

    def print_grammar(self, number_lines = True): # pragma: nocover
        """Prints the grammar (with line numbers)

        Args:
            number_lines (bool): if ``False`` line numbers will not be printed.
        """
        if number_lines:
            print('\n'.join(map(lambda n_r: '{:3}:\t{}'.format(n_r[0], n_r[1]), enumerate(self.grammar.splitlines(), 1))))
        else:
            print(self.grammar)

    def context(self, text, symbol, trace = False, diag = False, build_parse_trees = True, as_string = False, fail_on_error = False):
        """Returns an object subclass of a ``antlr4.ParserRuleContext`` corresponding to the specified symbol (possibly as a string).

        Args:
            text (str): the text to be parsed.
            symbol (str): the symbol (rule name) the parse should start at.
            trace (bool): if ``True`` the method ``antlr4.Parser.setTrace`` will be used to activate *tracing*.
            diag (bool): if ``True`` the parsing will be run with a ``antlr4.error.DiagnosticErrorListener`` setting the prediction mode to ``antlr4.atn.PredictionMode.LL_EXACT_AMBIG_DETECTION``.
            build_parse_trees (bool): if ``False`` the field ``antlr4.Parser.buildParseTrees`` will be set to ``False`` so that no trees will be generated.
            as_string (bool): if ``True`` the method will return the string representation of the context obtained using its ``toStringTree`` method.
            fail_on_error (bool): if ``True`` the method will return ``None`` in case of paring errors.

        Returns:
            A parser context, in case of parsing errors the it can be used to investigate the errors (unless ``fail_on_error`` is ``True`` in what case this method returns ``None``).
        """
        lexer = self.Lexer(InputStream(text))
        stream = CommonTokenStream(lexer)
        parser = self.Parser(stream)
        parser.setTrace(trace)
        if diag:
            parser.addErrorListener(DiagnosticErrorListener())
            parser._interp.predictionMode = PredictionMode.LL_EXACT_AMBIG_DETECTION
        parser.buildParseTrees = build_parse_trees
        buf = StringIO()
        with redirect_stderr(buf):
            ctx = getattr(parser, symbol)()
        errs = buf.getvalue().strip()
        if errs:
            warn(errs)
            if fail_on_error: return None
        if as_string:
            return ctx.toStringTree(recog = self.Parser)
        else:
            return ctx

    def tokens(self, text):
        """Returns a list of *tokens*.

        This method uses the *lexer* wrapped in a ``antlr4.CommonTokenStream`` to obtain the list of tokens (calling the ``fill`` method).

        Args:
            text (str): the text to be processed by the *lexer*.
        """
        lexer = self.Lexer(InputStream(text))
        stream = CommonTokenStream(lexer)
        stream.fill()
        return stream.tokens

    def tree(self, text, symbol, simple = False):
        """Returns an *annotated* :class:`~liblet.display.Tree` representing the parse tree (derived from the parse context).

        Unless a *simple* tree is required, the returned is an *annotated* tree whose nodes store
        context information from the parsing process, more precisely, nodes are :obj:`dicts <dict>` with the following keys:

        - ``type``: can be ``rule`` or ``token``,
        - ``name``: the *rule label* or *token name* (or the rule name if it has no label: or, similarly, the token itself if it has no name),
        - ``value``: the *token* value (only present for *tokens* named in the *lexer* part of the grammar),
        - ``rule``: the *rule* name (only present for *rules*, will be different from ``name`` for labelled rules).

        Note that the values are strings (so if the *value* is a number, it should be converted before usage).

        This method removes any ``<EOF>`` tree returned in the underlying parse tree (unless a simple tree is required).

        Args:
            text (str): the text to be parsed.
            symbol (str): the symbol (rule name) the parse should start at.
            simple (bool): if ``True`` the returned tree nodes will be strings (with no context information).
        Returns:
            :class:`liblet.display.Tree` the (possibly annotated) parse tree, or ``None`` in case of parsing errors.
        """

        def _rule(ctx):
            rule = self.Parser.ruleNames[ctx.getRuleIndex()]
            if simple:
                return rule
            else:
                name = ctx.__class__.__name__
                name = name[:-7] # remove trailing 'Context'
                name = name[0].lower() + name[1:]
                return {'type': 'rule', 'name': name, 'rule': rule}

        def _token(token):
            ts = token.symbol
            text = r'\\n' if ts.text == '\n' else ts.text
            if simple:
                return text
            else:
                try:
                    name = self.Parser.symbolicNames[ts.type]
                except IndexError:
                    name = '<INVALID>'
                if name == '<INVALID>':
                    name = self.Parser.literalNames[ts.type][1:-1]
                return {'type': 'token', 'name': name, 'value': text}

        class TreeVisitor(ParseTreeVisitor):
            def visitTerminal(self, t):
                if t.symbol.type == -1: return None
                return Tree(_token(t))
            def aggregateResult(self, result, childResult):
                if result is None: return [childResult]
                if childResult is None: return result
                result.append(childResult)
                return result
            def visitChildren(self, ctx):
                return Tree(_rule(ctx), super().visitChildren(ctx))

        ctx = self.context(text, symbol, fail_on_error = True)
        if ctx is None: return None
        return TreeVisitor().visit(ctx)

class AnnotatedTreeWalker:
    """A *dispatch table* based way to recursively walk an annotated tree.

    The aim of this class is to provide a convenient way to recursively apply
    functions to the subtrees of a given tree according to their root annotations.

    More precisely, once an object of this class is instantiated it can be used
    to *register* a set of functions named as the values of a specified *key*
    contained in the annotated tree root; trees that don't have a corresponding
    registered function are handled via a *catchall* function (few sensible
    defaults are provided).

    Once such functions are registered, the object can be used as a `callable <https://docs.python.org/3/reference/expressions.html?highlight=callable#calls>`__ and
    invoked on an annotated tree; this will lead to the recursive invocation of
    the registered (and the catchall) functions on subtrees. Such functions are
    invoked with the object as the first argument (and the subtree as second); in this
    way they can recurse on their subtrees as needed.

    Args:
        key (str): the key that will be looked up in the node :obj:`dict` to
                   determine which registered function to call.
        catchall (callable): the *catchall* function that will be invoked in case
                             the root is not a dict, or does not contain the key, or
                             no function has been registered for the value corresponding to the key.

    """

    @staticmethod
    def RECOURSE_CHILDREN(visit, tree):
        """A default *catchall* that will invoke the recursion on all the subtrees;
        this function does not emit any warning and does not return any value.
        """
        for child in tree.children: visit(child)

    @staticmethod
    def TREE_CATCHALL(visit, tree):
        """A default *catchall* that will invoke the recursion on all the subtrees, emitting
        a :meth:`~liblet.utils.warn` and returning a tree with the same root of the given tree
        and having as children the recursively visited children of the given tree."""
        warn('TREE_CATCHALL: {}'.format(tree.root))
        return Tree(tree.root, [visit(child) for child in tree.children])

    @staticmethod
    def TEXT_CATCHALL(visit, tree):
        """A default *catchall* that will invoke the recursion on all the subtrees, emitting
        a :meth:`~liblet.utils.warn` and returning a string with the same root of the given tree
        and having as children the (indented string representation of the) recursively visited
        children of the given tree."""
        warn('TEXT_CATCHALL: {}'.format(tree.root))
        return '{}'.format(tree.root) + ('\n' + indent('\n'.join(visit(child) for child in tree.children), '\t') if tree.children else '')

    def __init__(self, key, catchall = None):
        self.key = key
        self._catchall = catchall if catchall is not None else AnnotatedTreeWalker.TREE_CATCHALL
        self.DT = {}

    def catchall(self, func):
        """A :term:`decorator` used to register a *catchall* function.

        The decorated function must have two arguments: the first will be always an instance of this object, the
        second the annotate tree on which to operate. The previous registered *catchall* function will be overwritten.
        """
        self._catchall = func

    def register(self, func):
        """A :term:`decorator` used to register a function.

        The function will be registered with his name (possibly replacing a previous registration).
        The decorated function must have two arguments: the first will be always an instance of this object, the
        second the annotate tree on which to operate.
        """
        self.DT[func.__name__] = func

    def __call__(self, tree):
        key = tree.root[self.key]
        return self.DT[key](self.__call__, tree) if key in self.DT else self._catchall(self.__call__, tree)
