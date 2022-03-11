from itertools import count
from pathlib import Path
from subprocess import run, CalledProcessError, PIPE
from textwrap import dedent, indent

from graphviz import Source

from . import warn

from os import environ

LLVM_VERSION = environ.get('LLVM_VERSION')
if LLVM_VERSION is not None:
  OPT_EXECUTABLE = 'opt-{}'.format(LLVM_VERSION)
  CLANG_EXECUTABLE = 'clang-{}'.format(LLVM_VERSION)

def _run_clang(args, *, _ = None, **kwargs):
  if LLVM_VERSION is None: raise FileNotFoundError('Please define the LLVM_VERSION environment variable')
  try:
    return run([CLANG_EXECUTABLE] + args, **kwargs)
  except FileNotFoundError:
    raise FileNotFoundError('Executable {} not found, LLVM_VERSION is {}'.format(CLANG_EXECUTABLE, LLVM_VERSION)) from None

def _run_opt(args, *, _ = None, **kwargs):
  if LLVM_VERSION is None: raise FileNotFoundError('Please define the LLVM_VERSION environment variable')
  try:
    return run([OPT_EXECUTABLE] + args, **kwargs)
  except FileNotFoundError:
    raise FileNotFoundError('Executable {} not found, LLVM_VERSION is {}'.format(OPT_EXECUTABLE, LLVM_VERSION)) from None

WRAPPING_CODE = r"""
  ; ModuleID = '{name}.ll'
  source_filename = "{name}.ll"

  @.decfmt.0 = internal constant [3 x i8] c"%d\00"
  @.decfmt.1 = internal constant [4 x i8] c"%d\0A\00"

  declare i32 @__isoc99_scanf(i8*, ...)
  declare i32 @printf(i8*, ...)

  define i32 @input() {{
    %.1 = alloca i32
    %.2 = bitcast [3 x i8]* @.decfmt.0 to i8*
    %.3 = call i32 (i8*, ...) @__isoc99_scanf(i8* %.2, i32* %.1)
    %.4 = load i32, i32* %.1
    ret i32 %.4
  }}

  define void @print(i32 %0) {{
    %.1 = bitcast [4 x i8]* @.decfmt.1 to i8*
    %.2 = call i32 (i8*, ...) @printf(i8* %.1, i32 %0)
    ret void
  }}

  define void @main() {{
    entry:
    {code}
    ret void
  }}
"""


class LLVM:
  """An utility class to play with LLVM IR language"""

  def __init__(self, name, code = ''):
    self.name = name
    self._variable = count(0)
    self._label = count(0)
    self.code = []
    self.append_code(code)

  def new_variable(self):
    """Returns a new identifier for a variable."""
    return '%v{}'.format(next(self._variable))

  def new_label(self):
    """Returns a new identifier for a label."""
    return 'l{}'.format(next(self._label))

  def append_code(self, code):
    """Appends the given code."""
    if isinstance(code, str): code = dedent(code).splitlines()
    self.code.extend(filter(lambda _: _.strip() != '', code))

  def print_code(self):
    """Prints the unwrapped source collected code."""
    print('\n'.join(self.code))

  def write_and_compile(self):
    """Wraps the code in some boilerplate, writes it to disk and compiles it."""
    code = '\n' + indent('\n'.join(self.code), 16 * ' ') + '\n'
    wrapped = WRAPPING_CODE.format(name = self.name, code = code)
    Path(self.name).with_suffix('.ll').write_text(dedent(wrapped))
    Path(self.name).unlink(missing_ok = True)
    try:
      _run_clang('-Wno-override-module -o {name} {name}.ll'.format(name = self.name).split(), check = True, stdout = PIPE, stderr = PIPE)
    except CalledProcessError as e:
      warn(e.stderr.decode('utf8'))

  def control_flow_graph(self):
    """Returns the control flow graph."""
    self.write_and_compile()
    _run_opt('-analyze -o /dev/null -dot-cfg {name}.ll'.format(name = self.name).split())
    return Source(Path('.main.dot').read_text())

  def mem2reg(self):
    """Outputs the result of `mem2reg` optimization."""
    return _run_opt('-mem2reg -S {name}.ll'.format(name = self.name).split(), stdout = PIPE).stdout.decode('utf8')
