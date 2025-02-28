def install_antlrjar():
  FILE = 'antlr-4.13.2-complete.jar'
  URL = 'https://www.antlr.org/download/' + FILE

  from pathlib import Path
  from urllib.request import urlopen

  jars = Path('jars')
  jars.mkdir(exist_ok=True)
  with (jars / FILE).open('wb') as ouf, urlopen(URL) as inf:  # noqa: S310
    ouf.write(inf.read())

  print(f'Remember to add set ANTLR4_JAR="{(jars / FILE).resolve()}" in your environment')  # noqa: T201


if __name__ == '__main__':
  install_antlrjar()
