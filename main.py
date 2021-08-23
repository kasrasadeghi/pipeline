import os  # listdir, stat
import os.path  # isfile
import sys  # argv
import json  # load, dump
from functools import cache
import datetime
from subprocess import check_output

from flask import Flask, Response, render_template, escape, request, redirect

from pprint import pprint

app = Flask(__name__)

# LIB

class RemarkableNoteManager:
  root = "/home/kasra/projects/remarkable-kaz"

  def _temp(self, filename):
    return self.root + "/temp/" + filename

  @cache
  def namemap(self):
    with open(self._temp("namemap.data")) as f:
      namemap = json.load(f)
      uuidmap = {v: k for k, v in namemap.items()}
      return (namemap, uuidmap)

  @cache
  def notebooks(self):
    with open(self._temp("notebooks.data")) as f:
      return json.load(f)

  @cache
  def copied_uuids(self):
    return [x[:-len(".metadata")] for x in os.listdir("temp") if x.endswith("metadata")]

  @cache
  def pages(self):
    result = dict()
    for notebook_uuid in self.copied_uuids():
      with open(self._temp(f"{notebook_uuid}.content")) as f:
        data[notebook_uuid] = json.load(f)["pages"]
    return result

RM = RemarkableNoteManager()

# this class is a namespace
class util:
  @classmethod
  def sort_recent(_, files, root_path):
    return [p[0] for p in sorted([(f, os.stat(root_path +'/'+ f).st_mtime) for f in files], key = lambda p: p[1])]

  @classmethod
  def basename(_, filename):
    return filename.rsplit("/", 1)[1]


class FLAT:
  path = "/home/kasra/notes"

  @classmethod
  def list(cls):
    return [x for x in os.listdir(cls.path) if os.path.isfile(cls.path + "/" + x) and not (x[0] == '#' and x[-1] == '#')]

  @classmethod
  def listabs(cls):
    return list(map(lambda x: cls.path + "/" + x, cls.list()))

  @classmethod
  def to_url(_, note):
    return "/note/" + note

  @classmethod
  def to_path(cls, note):
    return cls.path + "/" + note

  @classmethod
  def parse(cls, content):
    lines = content.splitlines()
    acc = list()
    for L in lines:

      if "- note: " in L and len(L.split("- note:", 1)) == 2:
        before, note = L.split("- note: ", 1)
        acc.append(f'{before}- note: <a href="{cls.to_url(note)}">{note}</a>')
        continue

      if "- link: " in L and len(L.split("- link:", 1)) == 2:
        before, link = L.split("- link: ", 1)
        acc.append(f'{before}- link: <a href="{link}">{link}</a>')
        continue

      acc.append(L)

    return "\n".join(acc)

  @classmethod
  def collect_refs(cls, note):
    """@returns a list of notes this note references in the order they appear"""
    with open(cls.to_path(note)) as f:
      lines = f.readlines()

    acc = list()
    for L in lines:
      if "- note: " in L and len(L.split("- note:", 1)) == 2:
        note = L.split("- note: ", 1)[1].rstrip()
        acc.append(note)
        continue

    return acc

  @classmethod
  def backlinks_refmap(cls):
    refmap = dict()
    for note in FLAT.list():
      refmap[note] = list(set(FLAT.collect_refs(note)))

    backlinks = dict()  # maps from note to set of referrers
    for note, refs in refmap.items():
      for ref in refs:
        if ref not in backlinks:
          backlinks[ref] = set()
        backlinks[ref].add(note)

    return backlinks, refmap

  @classmethod
  def init_note(cls, note, title):
    datecmd=["date", "+%a %b %e %T %Z %Y"]  # from emacs/lisp/kaz.el's kaz/current-time
    with open(cls.to_path(note), "w+") as f:
      f.write("--- METADATA ---\n")
      f.write("Date: ")
      f.write(check_output(datecmd).decode('latin-1'))
      f.write(f"Title: {title}\n")

  @classmethod
  def edit(cls, note):
    cmd = f"emacsclient -c '{cls.to_path(note)}' & disown > /dev/null"
    os.system(cmd)

  @classmethod
  def make_new(cls, title):
    with open("/proc/sys/kernel/random/uuid") as uuid:
      note = uuid.read().strip() + ".note"
    if os.path.isfile(cls.to_path(note)):
      return "/try-again"
    else:
      with open(cls.to_path(note), "w+") as new_note:
        new_note.write("")
      cls.init_note(note, title)
      return note

  @classmethod
  def metadata(cls, note):
    with open(cls.to_path(note)) as f:
      reading = False
      acc = list()
      for l in f:
        if l == "--- METADATA ---\n":
          reading = True
          continue
        if reading == True:
          if l.startswith("---") and l.endswith("---\n"):
            reading = False
            continue
          if l.strip() != "":
            acc.append(l.rstrip())

    result = {p[0]: p[1].strip() for p in [x.split(":", 1) for x in acc]}
    return result

  @classmethod
  def title(cls, note):
    return cls.metadata(note)['Title']

  @classmethod
  def list_by_create_date(cls):
    def time_metadata(n):
      """get create time from metadata, translated from date '+%a %b %e %T %Z %Y' """
      return datetime.datetime.strptime(FLAT.metadata(n)['Date'], "%a %b %d %H:%M:%S %Z %Y")
    return [p[0] for p in sorted([(n, time_metadata(n)) for n in cls.list()], key = lambda p: p[1])]

class TAG:
  @classmethod
  def parse(_, l):
    tags = set(map(lambda s: s.strip(), l.split("=>", 1)[1].split(",")))
    return tags

# END LIB

# RENDER

class RENDER:
  @classmethod
  def STYLE(_):
    return """<style>
       * { font-size: clamp(2vmin, 1rem + 2vw, 24px); }
       body { margin: 1% 2%; }
     </style>"""


  @classmethod
  def TEXT(R, title, content):
    return Response(f"<!DOCTYPE hmtl><html><head>{R.STYLE()}<title>{title}</title></head>"
                    + f"<body><pre>{content}</pre></body></html>", mimetype="text/html")

  @classmethod
  def NOTE(R, note):
    # read file

    path = FLAT.to_path(note)
    content = list()

    if os.path.isfile(path):
      with open(path) as f:
        c = f.read()
        if not c.endswith("\n"):
          content.append("\n")
        content.append(c)
    content = "".join(content)

    # parse references and links in file
    content = FLAT.parse(content)

    # parse forward links
    def render_link(note):
      link = FLAT.to_url(note)
      return f'- <a href="{link}">{FLAT.title(note)}</a>'

    forward_links = ""
    forward_link_list = FLAT.collect_refs(note)
    if 0 != len(forward_link_list):
      forward_links = list()
      forward_links.append("\n\n--- LINKS ---\n")
      forward_links.append("\n".join(map(render_link, FLAT.collect_refs(note))))
      forward_links = "".join(forward_links)

    backlink_map = FLAT.backlinks_refmap()[0]
    backlinks = ""
    if note in backlink_map:
      backlinks = list()
      backlinks.append("\n\n--- BACKLINKS ---\n")
      backlinks.append("\n".join(map(render_link, list(backlink_map[note]))))
      backlinks = "".join(backlinks)

    # create bar
    bar = list()
    bar.append(f'<div style="display: flex;align-items:baseline">')
    bar.append(f'<form method="post"><button name="edit" value="{note}">edit</button></form>')
    bar.append(f'<button onclick="copy()">copy uuid</button>')
    bar.append(f'<a href="/">root</a>')
    bar.append(f'</div>')
    bar.append(f'<script>function copy() {{ navigator.clipboard.writeText("{note}"); }}</script>')
    bar = "".join(bar)

    # compose html
    title = FLAT.title(note)
    title_style = "margin-left: 1em; border-left: 2px black solid; border-bottom: 2px black solid; padding-left: 10px; padding-bottom: 6px"
    result = "".join([f"<!DOCTYPE hmtl><html><head>{R.STYLE()}<title>{title}</title></head>",
                      f"<body>{bar}<pre style='font-feature-settings: \"liga\" 0'>"
                      f'<h1 style="{title_style}">{title}</h1>'
                      f"{content}{forward_links}{backlinks}</pre></body></html>"])
    return Response(result, mimetype="text/html")


  @classmethod
  def LIST(R, items, title, linkfunc, colsfunc=lambda x: tuple(), namefunc=lambda x: x):
    """
    @param colsfunc - returns content for the other columns in this item's row
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

# END RENDER

# ROUTES

@app.route("/index.html")
def to_root():
  return redirect("/", code=302)

@app.route("/")
def get_root():
  if 'title' in request.args and len(request.args['title'].strip()) != 0:
    return redirect(FLAT.to_url(FLAT.make_new(title=request.args['title'].strip())), code=302)
  return render_template("index.html", style=RENDER.STYLE())

@app.route("/all")
def get_all():
  return RENDER.LIST(FLAT.list(), title="Notes", linkfunc=FLAT.to_url,
                     colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                     namefunc=FLAT.title)

@app.route("/recents")
def recents():
  return RENDER.LIST(reversed(util.sort_recent(files=FLAT.list(),
                                        root_path=FLAT.path)),
                     title="Recent Notes",
                     linkfunc=FLAT.to_url,
                     colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                     namefunc=FLAT.title)

@app.route("/creation")
def creation():
  """returns a list of notes by creation date"""
  return RENDER.LIST(reversed(FLAT.list_by_create_date()),
                     title="Recent Notes",
                     linkfunc=FLAT.to_url,
                     colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                     namefunc=FLAT.title)

@app.route("/journals")
def journal_list():
  return RENDER.LIST(reversed([x for x in FLAT.list_by_create_date() if 'Tags' in FLAT.metadata(x) and "Journal" in set(FLAT.metadata(x)['Tags'].split())]),
                     title="Journals",
                     linkfunc=FLAT.to_url,
                     colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                     namefunc=FLAT.title)

@app.route("/today")
def today():
  day_of_month = check_output(["date", "+%e"]).decode('latin-1').strip()
  day_of_month_suffix = {1:"st", 2:"nd", 3:"rd"}.get(int(day_of_month[-1]), "th")
  month, year = check_output(["date", "+%B %Y"]).decode('latin-1').rstrip().split()
  title = f"{month} {day_of_month}{day_of_month_suffix}, {year}"

  for n in FLAT.list():
    if title == FLAT.title(n):
      return redirect(FLAT.to_url(n), code=302)

  new_note = FLAT.make_new(title=title)
  with open(FLAT.to_path(new_note)) as f:
    content = f.read()
  with open(FLAT.to_path(new_note), "w") as f:
    f.write(f"# {month} {day_of_month}\n\n" + content + "Tags: Journal\n")
  return redirect(FLAT.to_url(new_note), code=302)

@app.route("/yesterday")
def yesterday():
  day_of_month = check_output(["date", "--date=yesterday", "+%e"]).decode('latin-1').strip()
  day_of_month_suffix = {1:"st", 2:"nd", 3:"rd"}.get(int(day_of_month[-1]), "th")
  month, year = check_output(["date", "--date=yesterday", "+%B %Y"]).decode('latin-1').rstrip().split()
  title = f"{month} {day_of_month}{day_of_month_suffix}, {year}"

  for n in FLAT.list():
    if title == FLAT.title(n):
      return redirect(FLAT.to_url(n), code=302)

  new_note = FLAT.make_new(title=title)
  with open(FLAT.to_path(new_note)) as f:
    content = f.read()
  with open(FLAT.to_path(new_note), "w") as f:
    f.write(f"# {month} {day_of_month}\n\n" + content + "Tags: Journal\n")
  return redirect(FLAT.to_url(new_note), code=302)


@app.route("/note/<note>", methods=['GET', 'POST'])
def get_note(note):
  if request.method == 'POST':
    FLAT.edit(note)
    return Response('', 204)
  else:
    assert note.endswith(".note")
    return RENDER.NOTE(note)

@app.route("/graph")
def get_graph():
  def title(note):
    if note in FLAT.list():
      return FLAT.title(note)
    else:
      return note

  def link(note):
    if note in FLAT.list():
      return f'<a href="{FLAT.to_url(note)}">{FLAT.title(note)}</a>'
    else:
      return note

  def legible_setdict(d):
    legible_result = list()
    for key, value in d.items():
      legible_result.append(link(key) + ":\n")
      ps = [(link(x), title(x)) for x in value]
      ps.sort(key=lambda p: p[1])
      for p in ps:
        legible_result.append("  " + p[0] + "\n")
    return "".join(legible_result)

  backlinks, refmap = FLAT.backlinks_refmap()

  limit = len(refmap)
  if 'limit' in request.args:
    limit = int(request.args.get('limit'))
  actual = list(refmap)[0:limit]

  unionfind = {x: x for x in actual}

  def find(note):
    if note == unionfind[note]:
      return note
    return find(unionfind[note])

  def union(note, other):
    other_rep = find(other)
    children = set()
    for child, parent in unionfind.items():
      if parent == other_rep:
        children.add(child)
    note_rep = find(note)
    for child in children:
      unionfind[child] = note_rep

  for note in actual:
    for other in refmap[note]:
      if other in actual and find(note) != find(other):
        union(note, other)

    if note in backlinks:
      for other in backlinks[note]:
        if other in actual and find(note) != find(other):
          union(note, other)

  result = dict()
  for key, value in unionfind.items():
    if value not in result:
      result[value] = set()
    result[value].add(key)

  return RENDER.TEXT("refs", legible_setdict(result))


@app.route("/rm/")
def get_rm_root():
  with open(f"/home/kasra/projects/remarkable-kaz/dist/index.html") as f:
    return Response(f.read(), mimetype="html")

@app.route("/rm/<rm>")
def get_rm(rm):
  with open(f"/home/kasra/projects/remarkable-kaz/dist/{rm}") as f:
    if rm.endswith("html"):
      return Response(f.read(), mimetype="html")
    return Response(f.read(), mimetype="image/svg+xml")

# END ROUTES

# MAIN

# don't run flask app in interactive prompt
if __name__ == "__main__" and not sys.__stdin__.isatty() and not 'EXEC_IMPORT' in dir():
  app.run()
