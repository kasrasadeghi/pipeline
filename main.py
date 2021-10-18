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

  def namemap(self):
    with open(self._temp("namemap.data")) as f:
      namemap = json.load(f)
      uuidmap = {v: k for k, v in namemap.items()}
      return (namemap, uuidmap)

  def notebooks(self):
    with open(self._temp("notebooks.data")) as f:
      return json.load(f)

  def copied_uuids(self):
    return [x[:-len(".metadata")] for x in os.listdir("temp") if x.endswith("metadata")]

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

  @classmethod
  def get_current_time(_):
    datecmd=["date", "+%a %b %e %T %Z %Y"]  # from emacs/lisp/kaz.el's kaz/current-time
    return check_output(datecmd).decode('latin-1')

  @classmethod
  def parse_time(_, time):
    """ translated from date '+%a %b %e %T %Z %Y' """
    return datetime.datetime.strptime(time, "%a %b %d %H:%M:%S %Z %Y")

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
  def to_disc(_, note):
    return note[:-len(".note")] + ".disc"

  @classmethod
  def to_path(cls, note):
    return cls.path + "/" + note

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
    with open(cls.to_path(note), "w+") as f:
      f.write("--- METADATA ---\n")
      f.write("Date: ")
      f.write(util.get_current_time())
      f.write(f"Title: {title}\n")

  @classmethod
  def open(cls, note):
    cmd = f"emacsclient -ca '{cls.to_path(note)}' & disown > /dev/null"
    os.system(cmd)

  @classmethod
  def edit(cls, note):
    cmd = f"emacsclient '{cls.to_path(note)}' & disown > /dev/null"
    os.system(cmd)

  @classmethod
  def chrome(cls, note):
    cmd = f"google-chrome-stable --app=http://localhost:5000" + FLAT.to_url(note)
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
      """get create time from metadata"""
      return util.parse_time(FLAT.metadata(n)['Date'])
    return [p[0] for p in sorted([(n, time_metadata(n)) for n in cls.list()], key = lambda p: p[1])]

  @classmethod
  def today(cls):
    day_of_month = check_output(["date", "+%e"]).decode('latin-1').strip()
    day_of_month_suffix = {1:"st", 2:"nd", 3:"rd"}.get(int(day_of_month[-1]), "th")
    month, year = check_output(["date", "+%B %Y"]).decode('latin-1').rstrip().split()
    title = f"{month} {day_of_month}{day_of_month_suffix}, {year}"

    for n in FLAT.list():
      if title == FLAT.title(n):
        return n

    new_note = FLAT.make_new(title=title)
    with open(FLAT.to_path(new_note)) as f:
      content = f.read()
    with open(FLAT.to_path(new_note), "w") as f:
      f.write(f"# {month} {day_of_month}\n\n" + content + "Tags: Journal\n")
    return new_note

  @classmethod
  def yesterday(cls):
    day_of_month = check_output(["date", "--date=yesterday", "+%e"]).decode('latin-1').strip()
    day_of_month_suffix = {1:"st", 2:"nd", 3:"rd"}.get(int(day_of_month[-1]), "th")
    month, year = check_output(["date", "--date=yesterday", "+%B %Y"]).decode('latin-1').rstrip().split()
    title = f"{month} {day_of_month}{day_of_month_suffix}, {year}"

    for n in FLAT.list():
      if title == FLAT.title(n):
        return n

    new_note = FLAT.make_new(title=title)
    with open(FLAT.to_path(new_note)) as f:
      content = f.read()
    with open(FLAT.to_path(new_note), "w") as f:
      f.write(f"# {month} {day_of_month}\n\n" + content + "Tags: Journal\n")
    return new_note

  @classmethod
  def handle_msg(_, note, form):
    msg = "- msg: " + form['msg'] + "\n  - Date: " + util.get_current_time() + "\n"

    # read note
    with open(FLAT.to_path(note), "r") as f:
      lines = f.readlines()

    # find metadata
    metadata_linenum = -1
    for i, l in reversed(list(enumerate(lines))):
      if l == "--- METADATA ---\n":
        metadata_linenum = i
    assert(metadata_linenum != -1)

    # write note with msg
    with open(FLAT.to_path(note), "w") as f:
      f.write("".join(lines[:metadata_linenum]))
      f.write(msg)
      f.write("".join(lines[metadata_linenum:]))

class PARSER:

  @classmethod
  def parse_ref(cls, L):
    tag = "- note: "
    if tag in L and len(L.split(tag, 1)) == 2:
      before, note = L.split(tag, 1)
      return True, f'{before}{tag}<a href="{FLAT.to_url(note)}">{note}</a>'
    else:
      return False, L

  @classmethod
  def parse_link(cls, L):
    tag = "- link: "
    if tag in L and len(L.split(tag, 1)) == 2:
      before, link = L.split(tag, 1)
      return True, f'{before}{tag}<a href="{link}">{link}</a>'
    else:
      return False, L

  @classmethod
  def parse(cls, content):
    lines = content.splitlines()
    acc = list()

    for L in lines:

      if (result := cls.parse_ref(L))[0]:
        acc.append(result[1])
        continue

      if (result := cls.parse_link(L))[0]:
        acc.append(result[1])
        continue

      acc.append(L)

    return "\n".join(acc)

  @classmethod
  def parse_disc(cls, content):
    lines = content.splitlines()
    acc = list()

    parse_msg = False
    msg = ""
    tmp_acc = list()

    for L in lines:

      if (result := cls.parse_ref(L))[0]:
        tmp_acc.append(result[1])
        continue

      if (result := cls.parse_link(L))[0]:
        tmp_acc.append(result[1])
        continue

      if L.startswith("- msg: "):
        if tmp_acc and "".join(tmp_acc) != "":
          acc.append("<pre>" + "\n".join(tmp_acc) + "</pre>")
        tmp_acc = list()

        msg = L.split("- msg: ")[1]
        parse_msg = True
        continue

      if parse_msg:
        assert L.startswith("  - Date: ")
        date = util.parse_time(L.split("- Date: ")[1])
        date = datetime.datetime.strftime(date, "%H:%M:%S")
        acc.append(f'<div class="msg"><div class="msg_timestamp">{date}</div><div class="msg_content">{escape(msg)}</div></div>')
        parse_msg = False
        msg = ""
        continue

      tmp_acc.append(L)

    if tmp_acc:
      acc.append("<pre>" + "\n".join(tmp_acc) + "</pre>")

    return "\n".join(acc)

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
             align-content: stretch; align-items: flex-start; overflow: hidden; }
       pre { margin: 0px; }
       .msg { display: flex; margin: 3px; font-family: monospace; }
       .msg_timestamp { border-radius: 18px; color: rgb(230, 50, 120); }
       .msg_content { padding: 7px 12px 8px 12px; border-radius: 18px; background-color: rgb(0, 130, 250); color: rgb(250, 250, 250);  }
       * { font-size: 18px; }

       .msg_input { width: -webkit-fill-available; margin: 5px}

       /* phones */
       @media (max-width: 1000px) {
         .msg { flex-direction: column; align-items: flex-start; }
         .msg_timestamp { margin: 0px 0px 0px 13px; padding: 5px 0px 1px 0px; }
       }

       /* desktop */
       @media (min-width: 1000px) {
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
    return Response(f"<!DOCTYPE hmtl><html><head>{R.STYLE()}<title>{title}</title></head>"
                    + f"<body><pre>{content}</pre></body></html>", mimetype="text/html")

  @classmethod
  def _read_file(R, note):
    acc = list()

    path = FLAT.to_path(note)
    if os.path.isfile(path):
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
    bar.append(f'<a style="margin-left: 10px" href="/today">today</a>')
    bar.append(f'<a style="margin-left: 10px" href="/yesterday">yesterday</a>')
    bar.append(f'<script>function copy() {{ navigator.clipboard.writeText("{note}"); }}</script>')

    for extra in extras:
      bar.append(extra)

    bar.append(f'</div>')
    return "".join(bar)

  @classmethod
  def NOTE(R, note):
    content = R._read_file(note)

    # parse references and links in file
    content = PARSER.parse(content)

    forward_links = R._section_forward_links(note)
    backlinks = R._section_backward_links(note)
    discussion = FLAT.to_disc(note)
    bar = R._bar(note, f'<a style="margin-left: 10px" href="/note/{discussion}">disc</a>')

    # compose html
    title = FLAT.title(note)
    title_style = "margin-left: 1em; border-left: 2px black solid; border-bottom: 2px black solid; padding-left: 10px; padding-bottom: 6px"
    result = "".join([f"<!DOCTYPE hmtl><html><head>{R.STYLE()}<title>{title}</title></head>",
                      f"<body>{bar}<pre style='font-feature-settings: \"liga\" 0'>",
                      f'<h1 style="{title_style}">{title}</h1>',
                      f"{content}{forward_links}{backlinks}</pre></body></html>"])
    return Response(result, mimetype="text/html")

  @classmethod
  def DISCUSSION(R, note):
    content = R._read_file(note)
    content = PARSER.parse_disc(content)

    forward_links = R._section_forward_links(note)
    backlinks = R._section_backward_links(note)
    bar = R._bar(note, f'<a style="margin-left: 10px" href="/note/{note}">note</a>')

    # compose html
    title = FLAT.title(note)
    title_style = "margin-left: 1em; border-left: 2px black solid; border-bottom: 2px black solid; padding-left: 10px; padding-bottom: 6px"
    result = "".join([f"<!DOCTYPE hmtl><html><head>{R.STYLE()}<title>{title}</title></head>",
                      f"<body>{bar}<div class=\"msgbox\" style='font-feature-settings: \"liga\" 0'>",
                      f'<h1 style="{title_style}">{title}</h1>',
                      f"{content}<pre>{forward_links}{backlinks}</pre></div>",
                      f'<form method="post"><input class="msg_input" autocomplete="off" autofocus type="text" name="msg"></form>',
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
         }

    ANSI = '\x1B['
    while True:
      s = chomp(ANSI)
      for code, replacement in D.items():
        if s.startswith(code):
          acc.append(replacement)
          s = s[len(code):]
          break
      else:
        print(f"ERROR: did not find replacement for ANSI code '{s[:5]}'")
        return original

      if s.find(ANSI) == -1:
        break

    return "".join(acc)


  @classmethod
  def _git_porcelain(R):
    status = check_output(['git', 'status', '--porcelain']).decode('utf8').strip()

    acc = list()

    for l in status.splitlines():
      if (i := l.rfind(".note")) != -1:
        before, uuid = l[:3], l[3:]  # 3 is the length of the annotation that git porcelain gives us
        acc.append((before, uuid))

    acc_sorted = reversed(sorted(acc, key=lambda p: util.parse_time(FLAT.metadata(p[1])['Date'])))

    acc = list()
    for (before, uuid) in acc_sorted:
      acc.append(before + f'<a href="/note/{uuid}">{FLAT.title(uuid)}</a>')

    status = "\n".join(acc)

    return status


  @classmethod
  def _git_status(R):
    status = check_output(['git', 'status']).decode('utf8').strip()

    UUID_LEN = len("2e62fd14-9b3a-4275-9a39-7bf3d6b488c7.note") # off by one lol

    acc = list()
    for l in status.splitlines():
      if (i := l.rfind(".note")) != -1:
        before, uuid = l[:-UUID_LEN], l[-UUID_LEN:]
        acc.append(before + f'<a href="/note/{uuid}">{FLAT.title(uuid)}</a>')
      else:
        acc.append(str(escape(l)))
    status = "\n".join(acc)

    return status

  @classmethod
  def _git_diff(R):
    # git color always: https://stackoverflow.com/questions/16073708/force-git-status-to-output-color-on-the-terminal-inside-a-script
    diff = check_output(['git', '-c', 'color.ui=always', 'diff']).decode('utf8').strip()
    diff = R._parse_color(str(escape(diff)))
    return diff

  @classmethod
  def GIT(R):
    title = "Git Status"
    header = f"<!DOCTYPE html><html><head>{R.STYLE()}<title>{title}</title></head><body>"

    currdir = os.getcwd()
    os.chdir('/home/kasra/notes')
    status = R._git_status()
    diff = R._git_diff()
    untracked_filenames = check_output(["git", "ls-files", "--others", "--exclude-standard"]).decode('utf8').strip()
    os.chdir(currdir)

    untracked_files = list()
    for l in untracked_filenames.splitlines():
      with open(FLAT.to_path(l)) as f:
        untracked_files.append(f.read())
      untracked_files[-1] = ('<span style="font-weight: bold">' + str(escape(l)) + "</span>\n" +
                             '<span style="color: green">' + str(escape(untracked_files[-1])) + "</span>\n")
    untracked = "".join(untracked_files)

    content = (f"<pre><h1>$ git status</h1>{status}</pre>" +
               "<div style='width: 90%; background-color: black; height: 2px; margin: 10px'></div>" +
               f"<pre><h1>$ git diff</h1>{diff}</pre>" +
               "<div style='width: 90%; background-color: black; height: 2px; margin: 10px'></div>" +
               f'<pre><h1>UNTRACKED FILES</h1>\n{untracked}</pre>')

    return Response(header + content  + "</body></html>", mimetype="text/html")

  @classmethod
  def GIT_MENU(R):
    title = "Git Status"
    header = f"<!DOCTYPE html><html><head>{R.STYLE()}<title>{title}</title></head><body>"

    currdir = os.getcwd()
    os.chdir('/home/kasra/notes')
    status = R._git_porcelain()
    os.chdir(currdir)

    content = (
      f"<pre><h1>$ git status --porcelain</h1>{status}</pre>")

    return Response(header + content  + "</body></html>", mimetype="text/html")


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

@app.route("/tag/<tag>")
def tag(tag):
  return RENDER.LIST(reversed([x for x in FLAT.list_by_create_date() if 'Tags' in FLAT.metadata(x) and tag in set(FLAT.metadata(x)['Tags'].split())]),
                     title="Tag: " + tag,
                     linkfunc=FLAT.to_url,
                     colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                     namefunc=FLAT.title)

@app.route("/git")
def git_status():
  return RENDER.GIT()

@app.route("/git/menu")
def git_menu():
  return RENDER.GIT_MENU()

@app.route("/today")
def today():
  return redirect(FLAT.to_url(FLAT.to_disc(FLAT.today())), code=302)

@app.route("/yesterday")
def yesterday():
  return redirect(FLAT.to_url(FLAT.to_disc(FLAT.yesterday())), code=302)

@app.route("/note/<note>", methods=['GET', 'POST'])
def get_note(note):

  # handle bar, which is in both discussion and note
  if request.method == 'POST':
    if 'open' in request.form:
      FLAT.open(request.form['open'])
      return Response('', 204)
    if 'edit' in request.form:
      FLAT.edit(request.form['edit'])
      return Response('', 204)


  # handle discussion
  if note.endswith(".disc"):
    note_id = note[:-len(".disc")]
    note = note_id + ".note"
    disc = note_id + ".disc"
    is_discussion = True

    # handle messages
    if request.method == 'POST':
      FLAT.handle_msg(note, request.form)
      return redirect(f"/note/{disc}", code=302)

    # default case: handle rendering
    return RENDER.DISCUSSION(note)


  # handle notes
  if note.endswith(".note"):
    # default case: handle rendering
    return RENDER.NOTE(note)


  # neither discussion nor note
  assert(False)

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

@app.route("/receive_info", methods=['POST'])
def receive_info():
  print(request.headers)
  print(request.json)
  return Response('', 204)

# END ROUTES

# MAIN

# don't run flask app in interactive prompt
if __name__ == "__main__" and not sys.__stdin__.isatty() and not 'EXEC_IMPORT' in dir():
  app.run()
