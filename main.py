import os  # listdir, stat
import os.path  # isfile
import sys  # argv
import json  # load, dump
import datetime
from subprocess import check_output

from flask import Flask, Response, render_template, escape, request, redirect

from pprint import pprint

app = Flask(__name__)

def kaz_import(filepath):
  with open(filepath) as f:
    exec(f.read(), globals())

# LIB

# this class is a namespace
class util:
  @classmethod
  def sort_recent(_, files, root_path):
    return [p[0] for p in sorted([(f, os.stat(root_path +'/'+ f).st_mtime) for f in files], key = lambda p: p[1])]

  @classmethod
  def basename(_, filename):
    return filename.rsplit("/", 1)[1]

  @classmethod
  def get_current_time(_):
    datecmd=["date", "+%a %b %e %T %Z %Y"]  # from emacs/lisp/kaz.el's kaz/current-time
    return check_output(datecmd).decode('latin-1')

  @classmethod
  def parse_time_to_utc(_, time):
    """
    translated from date '+%a %b %e %T %Z %Y'
    - used for comparisons and sorting
    """
    # convert the timezone to UTC because datetime in python doesn't handle timezones, omegalul
    clean_time = check_output(["date", "-d", time, "-u", "+%a %b %d %T %Z %Y"]).decode('utf8').strip()
    return datetime.datetime.strptime(clean_time, "%a %b %d %H:%M:%S %Z %Y")

  @classmethod
  def date_cmd(_, *l):
    return check_output(["date", *l]).decode('utf8').strip()

  @classmethod
  def read_file(R, filepath):

    if not os.path.isfile(filepath):
      print(f"ERROR: reading file that does not exist: '{filepath}'")
      return ""

    acc = list()

    with open(filepath) as f:
      c = f.read()
      if not c.endswith("\n"):
        acc.append("\n")
      acc.append(c)
    return "".join(acc)

# END LIB

# IMPORTS

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

kaz_import('sidebar.py')
kaz_import('render.py')
kaz_import('debug.py')

# END IMPORTS

# ROUTES

@app.route("/receive_info", methods=['POST'])
def receive_info():
  # print('client ip:', request.remote_addr)
  # print(request.headers)
  # print(request.json)
  return Response('', 204)

# END ROUTES

# MAIN

def main():
  app.run()

# don't run flask app in interactive prompt
if __name__ == "__main__" and not sys.__stdin__.isatty() and not 'EXEC_IMPORT' in dir():
  main()
