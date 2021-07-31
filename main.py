import os  # listdir, stat
import os.path  # isfile
import sys  # argv
import json  # load, dump
from functools import cache
from datetime import datetime, timezone
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
  def init_note(cls, note, title):
    datecmd=["date", "+%a %b %e %T %Z %Y"]  # from emacs kaz/current-time
    with open(cls.to_path(note), "w+") as f:
      f.write("--- METADATA ---\n")
      f.write("Date: ")
      f.write(check_output(datecmd).decode('latin-1'))
      f.write(f"Title: {title}\n")

  @classmethod
  def edit(cls, note):
    cmd = f"emacsclient {cls.to_path(note)} & disown > /dev/null"
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
            acc.append(l[:-1])

    result = {p[0]: p[1].strip() for p in [x.split(":", 1) for x in acc]}
    return result

class TAG:
  @classmethod
  def parse(_, l):
    tags = set(map(lambda s: s.strip(), l.split("=>", 1)[1].split(",")))
    return tags

# END LIB

# RENDER

class RENDER:
  @classmethod
  def TEXT(_, title, content):
    return Response(f"<!DOCTYPE hmtl><html><head><title>{title}</title></head>"
                    + f"<body><pre>{content}</pre></body></html>", mimetype="text/html")

  @classmethod
  def NOTE(_, note):
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

    # parse backlinks
    note_tag = note.split('.')[0]

    acc = list()
    for N in FLAT.listabs():
      with open(N) as f:
        for l in f:
          if "=>" in l:
            if note_tag in TAG.parse(l):
              acc.append(util.basename(N))

    def backlink(note):
      link = FLAT.to_url(note)
      return f'- <a href="/{link}">{note}</a>'

    backlinks = list()
    backlinks.append("\n--- BACKLINKS ---\n")
    backlinks.append("\n".join(map(backlink, acc)))

    # create bar
    bar = list()
    bar.append(f'<div style="display: flex;align-items:baseline">')
    bar.append(f'<form method="post"><button name="edit" value="{note}">edit</button></form>')
    bar.append(f'<button onclick="copy()">copy uuid</button>')
    bar.append(f'</div>')
    bar.append(f'<script>function copy() {{ navigator.clipboard.writeText("{note}"); }}</script>')
    bar = "".join(bar)

    # compose html
    title = note
    result = "".join([f"<!DOCTYPE hmtl><html><head><title>{title}</title></head>",
                      f"<body>{bar}<pre style='font-feature-settings: \"liga\" 0'>{content}{''.join(backlinks)}</pre></body></html>"])
    return Response(result, mimetype="text/html")


  @classmethod
  def LIST(_, items, title, linkfunc, colsfunc=lambda x: tuple(), namefunc=lambda x: x):
    """
    @param colsfunc - returns content for the other columns in this item's row
    """
    style="<style>* { font-family: monospace}</style>"
    header = f"<!DOCTYPE html><html><head><title>{title}</title></head><body>"
    body = "<table>"
    for i in items:
      columns = "".join(map(lambda x: "<td>" + x + "</td>", colsfunc(i)))
      body += f'<tr><td><a href="{linkfunc(i)}">{namefunc(i)}</a></td>{columns}</li>'
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
  return render_template("index.html")

@app.route("/all")
def get_all():
  return RENDER.LIST(FLAT.list(), title="Notes", linkfunc=FLAT.to_url,
                     colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                     namefunc=lambda x: FLAT.metadata(x)['Title'])

@app.route("/recents")
def recents():
  def flat_date(x):
    mtime = os.stat(FLAT.path + "/" + x).st_mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d")

  return RENDER.LIST(reversed(util.sort_recent(files=FLAT.list(),
                                        root_path=FLAT.path)),
                     title="Recent Notes",
                     linkfunc=FLAT.to_url,
                     colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                     namefunc=lambda x: FLAT.metadata(x)['Title'])

@app.route("/daily")
def daily():
  return RENDER.TEXT("daily", "daily")

@app.route("/note/<note>", methods=['GET', 'POST'])
def get_note(note):
  if request.method == 'POST':
    FLAT.edit(note)
    return Response('', 204)
  else:
    assert note.endswith(".note")
    return RENDER.NOTE(note)

@app.route("/rm/<rm>")
def get_rm(rm):
  with open(f"/home/kasra/projects/remarkable-kaz/dist/{note}.svg") as f:
    return Response(f.read(), mimetype="image/svg+xml")

# END ROUTES

# MAIN

# don't run flask app in interactive prompt
if __name__ == "__main__" and not sys.__stdin__.isatty():
  app.run()
