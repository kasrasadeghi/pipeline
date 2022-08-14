import os  # listdir, stat
import os.path  # isfile
import sys  # argv
import json  # load, dump
import datetime
from subprocess import check_output

from flask import Flask, Response, render_template, escape, request, redirect

app = Flask(__name__)

def kaz_import(filepath):
  with open(filepath) as f:
    compiled = compile(f.read(), filepath, 'exec')
    exec(compiled, globals())

# IMPORTS

kaz_import('magic.py')
kaz_import('util.py')
kaz_import('flask_util.py')

kaz_import('node.py')

kaz_import('flat.py')
kaz_import('git.py')
kaz_import('journal.py')
kaz_import('graph.py')
kaz_import('rm.py')

kaz_import('command.py')
kaz_import('commands/new_note.py')
kaz_import('commands/twitch_clip.py')

kaz_import('edit.py')
kaz_import('discussion.py')
kaz_import('parser.py')
kaz_import('tree.py')
kaz_import('plan.py')
kaz_import('search.py')
kaz_import('blog.py')

kaz_import('sidebar.py')
kaz_import('render.py')
kaz_import('debug.py')

# END IMPORTS

# MAIN

def main():
  app.run()

# don't run flask app in interactive prompt
if __name__ == "__main__" and not sys.__stdin__.isatty() and not 'EXEC_IMPORT' in dir():
  main()
