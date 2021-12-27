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

# RENDER
class RENDER:
  @classmethod
  def STYLE(_):
    # old font size: clamp(2vmin, 1rem + 2vw, 24px);
    # .msg_content: overflow: hidden; text-overflow: ellipsis;
    # .msg: overflow: hidden; max-width: 100%;
    navbar_size = 40 # in pixels
    header_color = "#bb6"
    link_button_color = "orange"
    msg_color = "#a52a2a"
    nav_button_color = "#611"
    base_text_color = "#ddd"
    input_background_color = "#333"
    return """
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <style>
       body { margin: 0; background: #222; }
       .content { padding-top: """ + str(navbar_size) + """px; margin: 0% 2% 1% 2%; }
       .msgbox { margin: 0px;
             display: flex; flex-direction: column;
             align-content: stretch; align-items: flex-start; }
       pre { margin: 0px; color: """ + base_text_color + """; }
       .msg { display: flex; margin: 3px; font-family: monospace; }
       .msg_timestamp { border-radius: 18px; color: rgb(230, 50, 120); }
       .msg_content { padding: 7px 12px 8px 12px; border-radius: 18px; background: """ + msg_color + """; color: rgb(250, 250, 250); overflow-wrap: anywhere;}
       * { font-size: 18px; color: """ + base_text_color + """; }
       header {
         display: flex; align-items:baseline;
         position: fixed; width: 100%; height: """ + str(navbar_size) + """px;
         background: """ + header_color + """; z-index: 12;
         margin: 0px;
         box-shadow: 0px 0px 11px 2px """ + header_color + """;
       }
       header > a {
         margin: 5px;
         padding: 0px 5px;
         color: """ + nav_button_color + """
       }

       .link-button {
         background: none;
         color: """ + link_button_color + """;
         cursor: pointer;
         font-family: monospace;
         border: """ + link_button_color + """ 1px solid;
         margin: 2px;
         padding: 6px 6px 4px 6px;
       }
       .link-button:focus { outline: none; }
       .link-button:active { color:red; }

       .msg_input { background: """ + input_background_color + """;width: -webkit-fill-available; margin: 5px}

       /* phones */
       @media (max-aspect-ratio: 1/1) {
         .msg { flex-direction: column; align-items: flex-start; }
         .msg_timestamp { margin: 0px 0px 0px 13px; padding: 5px 0px 1px 0px; }
       }

       /* desktop */
       @media (min-aspect-ratio: 1/1) {
         .msg { flex-direction: row; align-items: baseline; }
         .msg_timestamp { margin: 0px 5px 0px 0px; }
       }
     </style>""" + f"""<script>
       fetch("http://{request.headers['Host']}/receive_info",
         {{ method: "POST",
            headers: {{ 'Content-Type': 'application/json'}},
            body: JSON.stringify({{width: window.screen.width, height: window.screen.height, dpr: window.devicePixelRatio }})
         }}
       )
     </script>"""

  @classmethod
  def ANSI(R):
    return '\x1B['

  @classmethod
  def _parse_color(R, s):
    original = s

    acc = list()

    # chomp until the needle in the haystack
    def chomp(needle):
      before, after = s.split(needle, 1)
      acc.append(before)
      return after

    D = {'31m': '<span style="color:red">',
         'm': '</span>',
         '1m': '<span style="font-weight: bold">',
         '36m': '<span style="color:blue">',
         '1;36m': '<span style="font-weight:bold; color:#00b9f9">',
         '1;32m': '<span style="font-weight:bold; color:green">',
         '1;31m': '<span style="font-weight:bold; color:red">',
         '33m': '<span style="color:orange">',
         '32m': '<span style="color:green">',
         '7;31m': '<span style="background-color:red">',
         }

    ANSI = R.ANSI()
    while True:
      if -1 == s.find(ANSI):
        break

      s = chomp(ANSI)
      for code, replacement in D.items():
        if s.startswith(code):
          acc.append(replacement)
          s = s[len(code):]
          break
      else:
        print(f"ERROR: did not find replacement for ANSI code '{s[:5]}'")
        return original

    acc.append(s)

    return "".join(acc)

  # TODO CONSIDER making an "uncolored" function, that takes away the ascii
  #               codes OR the coloring spans from a string

  @classmethod
  def bar(cls):
    return "<div style='width: 90%; background-color: white; height: 2px; margin: 10px'></div>"

  @classmethod
  def nav(R, *extras):
    navbar = list()
    navbar.append(f'<header>'
                  f'<a style="" href="/">root</a>'
                  f'<a href="/today">today</a>'
                  f'<a href="/yesterday">yesterday</a>'
                  f'<a href="/git/menu">git</a>')

    for extra in extras:
      navbar.append(extra)

    navbar.append(f'</header>')
    return "".join(navbar)


# END RENDER

# ROUTES

kaz_import('flat.py')
kaz_import('git.py')
kaz_import('journal.py')
kaz_import('graph.py')
kaz_import('rm.py')

kaz_import('discussion.py')
kaz_import('parser.py')
kaz_import('plan.py')
kaz_import('search.py')


@app.route("/receive_info", methods=['POST'])
def receive_info():
  print('client ip:', request.remote_addr)
  print(request.headers)
  print(request.json)
  return Response('', 204)

# END ROUTES

# MAIN

# don't run flask app in interactive prompt
if __name__ == "__main__" and not sys.__stdin__.isatty() and not 'EXEC_IMPORT' in dir():
  app.run()
