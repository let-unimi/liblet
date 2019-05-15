from contextlib import redirect_stderr
from importlib import util as imputil
from io import StringIO
from os import environ
from os.path import join as pjoin, exists
from re import findall
from subprocess import run
from sys import modules
from tempfile import TemporaryDirectory

from antlr4.atn.PredictionMode import PredictionMode
from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.error.DiagnosticErrorListener import DiagnosticErrorListener
from antlr4.InputStream import InputStream
from antlr4.tree.Tree import ParseTreeVisitor

from .display import Tree, warn

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
            print(grammar)

    def context(self, text, symbol, trace = False, diag = False, build_parse_trees = True, as_string = False):
        """Returns an object subclass of a ``antlr4.ParserRuleContext`` corresponding to the specified symbol (possibly as a string).

        Args:
            text (str): the text to be parsed.
            symbol (str): the symbol (rule name) the parse should start at.
            trace (bool): if ``True`` the method ``antlr4.Parser.setTrace`` will be used to activate *tracing*.
            diag (bool): if ``True`` the parsing will be run with a ``antlr4.error.DiagnosticErrorListener`` setting the prediction mode to ``antlr4.atn.PredictionMode.LL_EXACT_AMBIG_DETECTION``.
            build_parse_trees (bool): if ``False`` the field ``antlr4.Parser.buildParseTrees`` will be set to ``False`` so that no trees will be generated.
            as_string (bool): if ``True`` the method will return the string representation of the context obtained using its ``toStringTree`` method.
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
        if errs: warn(errs)
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
        """Returns an *annotated* :obj:`~liblet.display.Tree` representing the parse tree (derived from the parse context).

        Unless a *simple* tree is required, the returned is an *annotated* tree whose nodes store
        context information from the parsing process, more precisely, nodes are :obj:`dicts <dict>` with the following keys:
        
        - ``type``: can be ``rule`` or ``token``,
        - ``name``: the grammar *rule* or *token* name (or the token itself, if it has no name),
        - ``value``: the *token* value (only present for *tokens* named in the *lexer* part of the grammar),
        - ``label``: the *rule* label (only present for *rules*, it the rule is not labelled, the rule name is used).

        Note that the values are strings (so if the *value* is a number, it should be converted before usage).

        Args:
            text (str): the text to be parsed.
            symbol (str): the symbol (rule name) the parse should start at.
            simple (bool): if ``True`` the returned tree nodes will be strings (with no context information).
        """

        def _rule(ctx):
            name = self.Parser.ruleNames[ctx.getRuleIndex()]
            if simple:
                return name
            else:
                label = ctx.__class__.__name__
                label = label[:-7] # remove trailing 'Context'
                label = label[0].lower() + label[1:]
                return {'type': 'rule', 'name': name, 'label': label}

        def _token(token):
            ts = token.symbol
            text = r'\\n' if ts.text == '\n' else ts.text
            if simple:
                return text
            else:
                name = self.Parser.symbolicNames[ts.type]
                if name == '<INVALID>': 
                    return {'type': 'token', 'name': self.Parser.literalNames[ts.type][1:-1]}
                else:
                    return {'type': 'token', 'name': name, 'value': text}

        class TreeVisitor(ParseTreeVisitor):
            def visitTerminal(self, t):
                return Tree(_token(t))
            def aggregateResult(self, result, childResult):
                if result is None: return [childResult]
                result.append(childResult)
                return result
            def visitChildren(self, ctx):
                return Tree(_rule(ctx), super().visitChildren(ctx))

        return TreeVisitor().visit(self.context(text, symbol))
