def install_antlrjar():

    FILE = 'antlr-4.7.2-complete.jar'
    URL = 'https://www.antlr.org/download/' + FILE

    from pathlib import Path
    from urllib.request import urlopen
    jars = Path('jars')
    jars.mkdir(exist_ok = True)
    with (jars / FILE).open('wb') as ouf:
        with urlopen(URL) as inf: ouf.write(inf.read())

    print(f'Remember to add set ANTLR4_JAR="{(jars / FILE).resolve()}" in your environment')

if __name__ == '__main__':
    install_antlrjar()