VERSION = "v1.0.1"

import os  # listdir, stat, getpid
import os.path  # isfile
import sys  # argv, exit
import json  # load, dump, dumps
import subprocess  # check_output, run

from flask import Flask, Response, render_template, escape, request, redirect, g

app = Flask(__name__)
# from werkzeug.middleware.profiler import ProfilerMiddleware
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, stream=None, profile_dir='profile-dumps')
# profiler slows down the app 3x ??

def kaz_import(filepath):
  from pathlib import Path
  path = Path(__file__).parent.absolute()
  with open(path / filepath) as f:
    compiled = compile(f.read(), filepath, 'exec')
    exec(compiled, globals())

# IMPORTS

kaz_import('device.py')
kaz_import('util.py')
kaz_import('flask_util.py')
kaz_import('tree_parser.py')
kaz_import('block_parser.py')
kaz_import('tree.py')
kaz_import('rewrite.py')
kaz_import('quote.py')

kaz_import('render.py')
kaz_import('render_util.py')
kaz_import('sidebar.py')

kaz_import('pattern.py')
kaz_import('date.py')
kaz_import('tag.py')

kaz_import('api.py')
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
kaz_import('modules/tv_brightness.py')

kaz_import('debug.py')
kaz_import('pretty.py')
kaz_import('unit_tests.py')

kaz_import('datecalc.py')

kaz_import('tools/latency.py')
kaz_import('tools/pagesize.py')
kaz_import('tools/profiler.py')
kaz_import('tools/merge.py')

# END IMPORTS

# MAIN

def main():
  app.run()

import signal

def handle_kill(signum, frame):
  signame = signal.Signals(signum).name
  with open('process.pid', 'a+') as f:
    f.write(f"- killed at {DATE.now()} by {signame} ({signum})\n")
    f.flush()
  with open('process.pid') as f:
    print(f.read())
  sys.exit(1)

def init_handle_kill():
  signal.signal(signal.SIGINT, handle_kill)
  signal.signal(signal.SIGTERM, handle_kill)

with open('process.pid', 'w+') as f:
  f.write(f"pid {os.getpid()} started at {DATE.now()}\n")  # TODO make this port specific
init_handle_kill()

# don't run flask app in interactive prompt
if __name__ == "__main__" and not sys.__stdin__.isatty() and not 'EXEC_IMPORT' in dir():
  main()
