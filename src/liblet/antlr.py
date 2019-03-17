from importlib import util as imputil
from os import environ, mkdir
from os.path import join as pjoin, exists
from subprocess import run
from sys import modules, stderr
from tempfile import TemporaryDirectory

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from antlr4.tree.Tree import ParseTreeVisitor

from .display import Tree

if not 'READ_THE_DOCS' in environ:
    if 'ANTLR4_JAR' not in environ:
        raise ImportError('Please define the ANTLR4_JAR environment variable')
    if not exists(environ['ANTLR4_JAR']):
        raise ImportError('The ANTLR4_JAR environment variable points to "{}" that is not an existing file'.format(environ['ANTLR4_JAR']))

def generate_and_load(name, grammar):
    with TemporaryDirectory() as tmpdir:
        
        with open(pjoin(tmpdir, name) + '.g', 'w') as ouf: ouf.write(grammar)        
        res = run([
            'java', '-jar', environ['ANTLR4_JAR'], 
             '-Dlanguage=Python3',
            '-listener', '-visitor',
            '{}.g'.format(name)
        ], capture_output = True, cwd = tmpdir)
        if res.returncode:
            stderr.write(res.stderr)
            return None

        res = {}
        for suffix in 'Lexer', 'Parser', 'Visitor', 'Listener':
            qn = '{}{}'.format(name, suffix)
            if qn in modules: del modules[qn]
            spec = imputil.spec_from_file_location(qn, pjoin(tmpdir, qn) + '.py')
            module = imputil.module_from_spec(spec)
            spec.loader.exec_module(module)
            modules[qn] = module
            res[suffix] = getattr(module, qn)
        return type(name, (object,), res)

def parse_tree(text, start, grammar_obj):
    lexer = grammar_obj.Lexer(InputStream(text))
    stream = CommonTokenStream(lexer)
    parser = grammar_obj.Parser(stream)
    return getattr(parser, start)()

def to_let_tree(tree, symbolic = False):

    RULE_NAMES = tree.parser.ruleNames
    
    def tokenName(ttype):
        symbolic = tree.parser.symbolicNames[ttype]
        if symbolic == '<INVALID>':
            return tree.parser.literalNames[ttype]
        else:
            return symbolic

    class TreeVisitor(ParseTreeVisitor):
        def visitTerminal(self, t):
            if symbolic:
                name = '{} ({})'.format(tokenName(t.symbol.type), r'\\n' if t.symbol.text == '\n' else t.symbol.text)
            else:
                name = r'\\n' if t.symbol.text == '\n' else t.symbol.text
            return Tree(name)
        def aggregateResult(self, result, childResult):
            if result is None: return [childResult]
            result.append(childResult)
            return result
        def visitChildren(self, ctx):
            return Tree(RULE_NAMES[ctx.getRuleIndex()], super().visitChildren(ctx))

    tv = TreeVisitor()
    return tv.visit(tree)
