import os  # listdir, stat
import os.path  # isfile
import sys  # argv
import json  # load, dump
from functools import cache
from datetime import datetime, timezone

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
  path = "/home/kasra/notes/new"

  @classmethod
  def list(cls):
    return os.listdir(cls.path)

  @classmethod
  def listabs(cls):
    return list(map(lambda x: cls.path + "/" + x, os.listdir(cls.path)))

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

      if "- note:" in L:
        before, note = L.split("- note: ", 1)
        acc.append(f'{before}- note: <a href="{cls.to_url(note)}">{note}</a>')
        continue

      if "- link:" in L:
        L.split("- link: ", 1)[1]
        continue

      acc.append(L)

    return "\n".join(acc)

  @classmethod
  def make_new(cls):
    with open("/proc/sys/kernel/random/uuid") as uuid:
      f = uuid.read().strip() + ".note"
    if os.path.isfile(cls.to_path(f)):
      return "/try-again"
    else:
      with open(cls.to_path(f), "w+") as new_note:
        new_note.write("")
      return cls.to_url(f)

class TAG:
  @classmethod
  def parse(_, l):
    tags = set(map(lambda s: s.strip(), l.split("=>", 1)[1].split(",")))
    print(tags)
    return tags

# END LIB

# RENDER

class RENDER:
  @classmethod
  def TEXT(_, title, content):
    return Response(f"<!DOCTYPE hmtl><html><head><title>{title}</title></head>"
                    + f"<body><pre>{content}</pre></body></html>", mimetype="text/html")

  @classmethod
  def TEXTFILE(cls, note):
    with open(FLAT.to_path(note)) as f:
      return cls.TEXT(note, f.read())

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

    # compose html
    title = note
    result = "".join([f"<!DOCTYPE hmtl><html><head><title>{title}</title></head>",
                      f"<body><pre>{content}{''.join(backlinks)}</pre></body></html>"])
    return Response(result, mimetype="text/html")


  @classmethod
  def LIST(_, items, title, linkfunc, colsfunc=lambda x: tuple()):
    """
    @param colsfunc - returns content for the other columns in this item's row
    """
    style="<style>* { font-family: monospace}</style>"
    header = f"<!DOCTYPE html><html><head><title>{title}</title></head><body>"
    body = "<table>"
    for i in items:
      columns = "".join(map(lambda x: "<td>" + x + "</td>", colsfunc(i)))
      body += f'<tr><td><a href="{linkfunc(i)}">{i}</a></td>{columns}</li>'
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
  if 'note' in request.args and request.args['note'] == 'new':
    return redirect(FLAT.make_new(), code=302)
  return render_template("index.html")

@app.route("/all")
def get_all():
  print(len(FLAT.list()))
  return RENDER.LIST(FLAT.list(), title="Notes", linkfunc=FLAT.to_url)

@app.route("/recents")
def recents():
  def flat_date(x):
    mtime = os.stat(FLAT.path + "/" + x).st_mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d")


  pprint(FLAT.list())

  return RENDER.LIST(reversed(util.sort_recent(files=FLAT.list(),
                                        root_path=FLAT.path)),
              title="Recent Notes",
              linkfunc=FLAT.to_url,
              colsfunc=lambda x: (flat_date(x),))

@app.route("/daily")
def daily():
  return RENDER.TEXT("daily", "daily")

@app.route("/note/<note>")
def get_note(note):
  if note.endswith(".note"):
    return RENDER.NOTE(note)
  else:
    return RENDER.TEXTFILE(note)

@app.route("/rm/<rm>")
def get_rm(rm):
  with open(f"/home/kasra/projects/remarkable-kaz/dist/{note}.svg") as f:
    return Response(f.read(), mimetype="image/svg+xml")

# END ROUTES

# MAIN

# don't run flask app in interactive prompt
if __name__ == "__main__" and not sys.__stdin__.isatty():
  app.run()
