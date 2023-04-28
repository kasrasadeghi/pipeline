import os  # listdir, stat
import os.path  # isfile
import sys  # argv
import json  # load, dump, dumps
from subprocess import check_output

from flask import Flask, Response, render_template, escape, request, redirect, g

app = Flask(__name__)
from werkzeug.middleware.profiler import ProfilerMiddleware
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, stream=None, profile_dir='profile-dumps')

def kaz_import(filepath):
  with open(filepath) as f:
    compiled = compile(f.read(), filepath, 'exec')
    exec(compiled, globals())

# IMPORTS

kaz_import('util.py')
kaz_import('flask_util.py')
kaz_import('tree_parser.py')
kaz_import('block_parser.py')
kaz_import('tree.py')
kaz_import('rewrite.py')
kaz_import('render.py')
kaz_import('render_util.py')
kaz_import('sidebar.py')
kaz_import('api.py')

kaz_import('pattern.py')
kaz_import('date.py')
kaz_import('tag.py')

kaz_import('flat.py')
kaz_import('search.py')
kaz_import('journal.py')
kaz_import('edit.py')
kaz_import('discussion.py')

kaz_import('dump.py')
kaz_import('outgoing.py')

kaz_import('git.py')
kaz_import('js.py')

kaz_import('command.py')  # exports @COMMAND.REGISTER
kaz_import('commands/new_note.py')
kaz_import('commands/full_sync.py')

kaz_import('commands/ytdl.py')

kaz_import('graph.py')

kaz_import('advanced_tree_parser.py')
kaz_import('modules/blog.py')
kaz_import('modules/fbconv.py')
kaz_import('modules/quant.py')
kaz_import('modules/loc.py')

kaz_import('debug.py')
kaz_import('pretty.py')
kaz_import('unit_tests.py')

kaz_import('tools/latency.py')
kaz_import('tools/pagesize.py')
kaz_import('tools/profiler.py')

# END IMPORTS

# MAIN

def main():
  app.run()

# don't run flask app in interactive prompt
if __name__ == "__main__" and not sys.__stdin__.isatty() and not 'EXEC_IMPORT' in dir():
  main()
