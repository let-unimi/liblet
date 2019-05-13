from importlib import util as imputil
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

from .display import warn

if not 'READTHEDOCS' in environ: # pragma: nocover
    if 'ANTLR4_JAR' not in environ:
        raise ImportError('Please define the ANTLR4_JAR environment variable')
    if not exists(environ['ANTLR4_JAR']):
        raise ImportError('The ANTLR4_JAR environment variable points to "{}" that is not an existing file'.format(environ['ANTLR4_JAR']))

class ANTLR:

    __slots__ = ('name', 'Lexer', 'Parser', 'Visitor', 'Listener', 'source') 

    def __init__(self, grammar):
        
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
                warn(str(res.stderr))
                return None

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

    def tree(self, text, symbol, trace = False, diag = False, buildParseTrees = True):
        lexer = self.Lexer(InputStream(text))
        stream = CommonTokenStream(lexer)
        parser = self.Parser(stream)
        parser.setTrace(trace)
        if diag:
            parser.addErrorListener(DiagnosticErrorListener())
            parser._interp.predictionMode = PredictionMode.LL_EXACT_AMBIG_DETECTION
        parser.buildParseTrees = buildParseTrees
        return getattr(parser, symbol)()

    def tokens(self, text):
        lexer = self.Lexer(InputStream(text))
        stream = CommonTokenStream(lexer)
        stream.fill()
        return stream.tokens

    def as_str(self, tree):
        return tree.toStringTree(recog = self.Parser)

    def as_lol(self, tree, symbolic = False):

        PARSER = self.Parser
        RULE_NAMES = PARSER.ruleNames
        
        def _name(token):
            ts = token.symbol
            text = r'\\n' if ts.text == '\n' else ts.text
            if symbolic:
                name = PARSER.symbolicNames[ts.type]
                if name == '<INVALID>': name = PARSER.literalNames[ts.type]
                return '{} [{}]'.format(name, text)
            else:
                return text

        class TreeVisitor(ParseTreeVisitor):
            def visitTerminal(self, t):
                return [_name(t)]
            def aggregateResult(self, result, childResult):
                if result is None: return [childResult]
                result.append(childResult)
                return result
            def visitChildren(self, ctx):
                return [RULE_NAMES[ctx.getRuleIndex()]] + super().visitChildren(ctx)

        return TreeVisitor().visit(tree)
