from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
    options = {'py2exe':{'skip_archive': True}},
    windows = [{'script': "py2exe_fixed.py"}],
    data_files = [('lib2to3', [r'C:/Python34/Lib/lib2to3/Grammar.txt', r'C:/Python34/Lib/lib2to3/PatternGrammar.txt'])]
                           # ('lib2to3', [r'C:/Python34/Lib/lib2to3/PatternGrammar.txt'])))
    #zipfile = "foo/library.zip",
)
#    zipfile="foo/bar.zip", 
#    options={"py2exe": {"skip_archive": True}})
