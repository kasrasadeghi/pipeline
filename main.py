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

kaz_import('flat.py')

# END LIB

# RENDER

class RENDER:

  @classmethod
  def STYLE(_):
    # old font size: clamp(2vmin, 1rem + 2vw, 24px);
    # .msg_content: overflow: hidden; text-overflow: ellipsis;
    # .msg: overflow: hidden; max-width: 100%;
    return """
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <style>
       body { margin: 1% 2%; }
       .msgbox { margin: 0px;
             display: flex; flex-direction: column;
             align-content: stretch; align-items: flex-start; }
       pre { margin: 0px; }
       .msg { display: flex; margin: 3px; font-family: monospace; }
       .msg_timestamp { border-radius: 18px; color: rgb(230, 50, 120); }
       .msg_content { padding: 7px 12px 8px 12px; border-radius: 18px; background-color: rgb(0, 130, 250); color: rgb(250, 250, 250); overflow-wrap: anywhere;}
       * { font-size: 18px; }

       .link-button {
         background: none;
         color: blue;
         cursor: pointer;
         font-family: monospace;
         border: blue 1px solid;
         margin: 2px;
         padding: 6px 6px 4px 6px;
       }
       .link-button:focus { outline: none; }
       .link-button:active { color:red; }

       .msg_input { width: -webkit-fill-available; margin: 5px}

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
  def TEXT(R, title, content):
    return Response(f"<!DOCTYPE hmtl><html><head>{RENDER.STYLE()}<title>{title}</title></head>"
                    + f"<body><pre>{content}</pre></body></html>", mimetype="text/html")

  @classmethod
  def _read_file(R, note):

    if not FLAT.exists(note):
      print(f"ERROR: reading note that does not exist: '{note}'")
      return ""

    acc = list()

    path = FLAT.to_path(note)
    with open(path) as f:
      c = f.read()
      if not c.endswith("\n"):
        acc.append("\n")
      acc.append(c)
    return "".join(acc)

  @classmethod
  def _render_link(R, note):
    link = FLAT.to_url(note)
    title = FLAT.title(note)
    return f'- <a href="{link}">{title}</a>'

  @classmethod
  def _section_forward_links(R, note):
    forward_link_list = FLAT.collect_refs(note)
    if 0 != len(forward_link_list):
      return "\n\n--- LINKS ---\n" + "\n".join([R._render_link(L) for L in forward_link_list])
    else:
      return ""

  @classmethod
  def _section_backward_links(R, note):
    backlink_map = FLAT.backlinks_refmap()[0]
    if note in backlink_map:
      return "\n\n--- BACKLINKS ---\n" + "\n".join([R._render_link(L) for L in backlink_map[note]])
    else:
      return ""

  @classmethod
  def _bar(R, note, *extras):
    bar = list()
    bar.append(f'<div style="display: flex;align-items:baseline">')
    bar.append(f'<form method="post">')
    bar.append(f'<button name="edit" value="{note}">edit</button>')
    bar.append(f'<button name="open" value="{note}">open</button>')
    bar.append(f'</form>')
    bar.append(f'<button onclick="copy()">copy uuid</button>')
    bar.append(f'<a style="margin-left: 10px" href="/">root</a>')
    bar.append(f'<span> </span>')
    bar.append(f'<a style="margin-left: 10px" href="/today">today</a>')
    bar.append(f'<span> </span>')
    bar.append(f'<a style="margin-left: 10px" href="/yesterday">yesterday</a>'
               f'<span> </span>'
               f'<a style="margin-left: 10px" href="/git/menu">git</a>')
    bar.append(f'<script>function copy() {{ navigator.clipboard.writeText("{note}"); }}</script>')

    for extra in extras:
      bar.append(extra)

    bar.append(f'</div>')
    return "".join(bar)

  @classmethod
  def NOTE(R, note):
    content = R._read_file(note)

    # parse references and links in file
    content = FLAT_PARSER.parse(content)

    forward_links = R._section_forward_links(note)
    backlinks = R._section_backward_links(note)

    bar = R._bar(note,
                 f'<span> </span>',
                 f'<a style="margin-left: 10px" href="/disc/{note}">disc</a>',
                 f'<span> </span>',
                 f'<a style="margin-left: 10px" href="/edit/{note}">edit</a>',
                 )

    # compose html
    title = FLAT.title(note)
    title_style = "margin-left: 1em; border-left: 2px black solid; border-bottom: 2px black solid; padding-left: 10px; padding-bottom: 6px; padding-right: 10px"
    result = "".join([f"<!DOCTYPE hmtl><html><head>{R.STYLE()}<title>{title}</title></head>",
                      f"<body>{bar}<pre style='font-feature-settings: \"liga\" 0'>",
                      f'<h1 style="{title_style}">{title}</h1>',
                      f"{content}{forward_links}{backlinks}</pre></body></html>"])
    return Response(result, mimetype="text/html")

  @classmethod
  def INDEX(R):
    note = FLAT.get_index()

    content = R._read_file(note)

    # parse references and links in file
    content = FLAT_PARSER.parse(content)

    bar = R._bar(note,
                 f'<span> </span>',
                 f'<a style="margin-left: 10px" href="/disc/{note}">disc</a>',
                 f'<span> </span>',
                 f'<a style="margin-left: 10px" href="/edit/{note}">edit</a>',
                 )

    # compose html
    title = FLAT.title(note)
    title_style = "margin-left: 1em; border-left: 2px black solid; border-bottom: 2px black solid; padding-left: 10px; padding-bottom: 6px; padding-right: 10px"
    result = "".join([f"<!DOCTYPE hmtl><html><head>{R.STYLE()}<title>{title}</title></head>",
                      f"<body>{bar}<pre style='font-feature-settings: \"liga\" 0'>",
                      f'<h1 style="{title_style}">{title}</h1>',
                      f"{content}</pre>",
                      f'<form><input style="width: 80%" type="text" name="title"><input type="submit" value="New Note"/></form>'
                      f"</body></html>"])
    return Response(result, mimetype="text/html")

  @classmethod
  def DISCUSSION(R, note):
    content = R._read_file(note)
    content = FLAT_PARSER.parse_disc(content)

    bar = R._bar(note,
                 f'<span> </span>',
                 f'<a style="margin-left: 10px" href="/note/{note}">note</a>'
                 f'<span> </span>'
                 f'<a style="margin-left: 10px" href="/edit/{note}">edit</a>'
                 )

    # compose html
    title = FLAT.title(note)
    title_style = "margin-left: 1em; border-left: 2px black solid; border-bottom: 2px black solid; padding-left: 10px; padding-bottom: 6px; padding-right: 10px"
    result = "".join([f"<!DOCTYPE hmtl><html><head>{R.STYLE()}<title>{title}</title></head>",
                      f"<body>{bar}<div class=\"msgbox\" style='font-feature-settings: \"liga\" 0'>",
                      f'<h1 style="{title_style}">{title}</h1>',
                      f"{content}</div>",
                      f'<form method="post"><input class="msg_input" autocomplete="off" autofocus type="text" name="msg"></form>',
                      f"</body></html>"])
    return Response(result, mimetype="text/html")

  @classmethod
  def EDIT(R, note):
    content = R._read_file(note)

    bar = R._bar(note,
                 f'<span> </span>',
                 f'<a style="margin-left: 10px" href="/note/{note}">note</a>'
                 f'<span> </span>',
                 f'<a style="margin-left: 10px" href="/disc/{note}">disc</a>'
                 )

    line_height = 23;

    textarea_resize_script = """
    function textarea_resize(el) {

      // https://stackoverflow.com/questions/15195209/how-to-get-font-size-in-html
      // https://stackoverflow.com/a/15195345
      linecount = el.innerHTML.split(/\\n/).length;
      el.style.height = (""" + str(line_height * 1.065) + """ * linecount)+"px";
    }
    // window.onload = () => { textarea_resize(document.getElementsByTagName("textarea")[0]); };
    """

    # compose html
    title = FLAT.title(note)
    title_style = "margin-left: 1em; border-left: 2px black solid; border-bottom: 2px black solid; padding-left: 10px; padding-bottom: 6px; padding-right: 10px"
    result = "".join([f"<!DOCTYPE hmtl><html><head>{R.STYLE()}<title>{title}</title></head>",
                      f"<body>{bar}",
                      f'<h1 style="{title_style}">{title}</h1>',
                      f'<script>{textarea_resize_script}</script>'
                      f'<form method="post">'
                      #f'<textarea name="text" oninput="textarea_resize(this)" style="line-height: 23px; resize:none; overflow: auto; width: -webkit-fill-available" rows="100">{content}</textarea><br/><br/>',
                      f'<textarea name="text" style="height: calc(85vh);line-height: 23px; resize:none; overflow: auto; width: -webkit-fill-available" rows="100">{content}</textarea><br/><br/>',
                      f'<input type="submit" value="Submit"/></form>',
                      f"</body></html>"])
    return Response(result, mimetype="text/html")

  @classmethod
  def LIST(R, items, title, linkfunc, colsfunc=lambda x: tuple(), namefunc=lambda x: x):
    """
    @param colsfunc - returns content for the other columns in this item's row in a list
    """
    header = f"<!DOCTYPE html><html><head>{R.STYLE()}<title>{title}</title></head><body>"
    body = """<table style="table-layout: fixed; width: 100%">"""
    for i in items:
      td_style = '"text-overflow: ellipsis; white-space: nowrap; overflow: hidden;"'
      columns = "".join(map(lambda x: f"<td style={td_style}>" + x + "</td>", colsfunc(i)))
      body += f'<tr><td style={td_style}><a href="{linkfunc(i)}">{namefunc(i)}</a></td>{columns}</li>'
    body += "</ul>"
    footer = "</body></html>"
    return Response(header + body + footer, mimetype="text/html")

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
         '32m': '<span style="color:green">',
         '7;31m': '<span style="background-color:red">',
         }

    ANSI = '\x1B['
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


    return "".join(acc)

# END RENDER

# ROUTES

@app.route("/index.html")
def to_root():
  return redirect("/", code=302)

@app.route("/")
def get_root():
  if 'title' in request.args and len(request.args['title'].strip()) != 0:
    return redirect(FLAT.to_url(FLAT.make_new(title=request.args['title'].strip())), code=302)

  return RENDER.INDEX()

kaz_import('git.py')
kaz_import('journal.py')
kaz_import('graph.py')
kaz_import('rm.py')

@app.route("/receive_info", methods=['POST'])
def receive_info():
  # print(request.headers)
  # print(request.json)
  return Response('', 204)

# END ROUTES

# MAIN

# don't run flask app in interactive prompt
if __name__ == "__main__" and not sys.__stdin__.isatty() and not 'EXEC_IMPORT' in dir():
  app.run()
