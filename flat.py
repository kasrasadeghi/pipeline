class FLAT:
  path = "/home/kasra/notes"

  @classmethod
  def list(cls):
    return [x for x in os.listdir(cls.path) if cls.exists(x) and not (x[0] == '#' and x[-1] == '#')]

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

  @staticmethod
  def try_from_url(url):
    host = request.headers["Host"]  # like 192.37.37.3:5000
    if url.startswith(f"http://{host}"):
      url = url.removeprefix(f"http://{host}")

    if url.startswith('/note/'):
      return url.removeprefix("/note/")
    if url.startswith('/disc/'):
      return url.removeprefix("/disc/")
    return url

  @classmethod
  def exists(cls, note):
    return os.path.isfile(cls.to_path(note))

  @classmethod
  def get_index(cls):
    return "4e0ce4ff-1663-49f9-8ced-30f91202ae08.note"  # hardcoded value, CONSIDER looking for "index" in Tags

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
    if cls.exists(cls.to_path(note)):
      return "/try-again"
    else:
      with open(cls.to_path(note), "w+") as new_note:
        new_note.write("")
      cls.init_note(note, title)
      return note

  @classmethod
  def metadata(cls, note):
    if not FLAT.exists(note):
      raise FileNotFoundError("cannot find notes file at " + note)

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
    return sorted(cls.list(), key=lambda n: util.parse_time_to_utc(FLAT.metadata(n)['Date']))

  @classmethod
  def today(cls):
    D = JOURNAL.date_to_parts(util.get_current_time())

    for n in FLAT.list():
      if D['title'] == FLAT.title(n):
        return n

    new_note = FLAT.make_new(title=D['title'])
    with open(FLAT.to_path(new_note)) as f:
      content = f.read()
    with open(FLAT.to_path(new_note), "w") as f:
      f.write(f"# {D['month']} {D['day_of_month']}\n\n{content}Tags: Journal\n")
    return new_note

  @classmethod
  def yesterday(cls):
    D = JOURNAL.date_to_parts("yesterday")

    for n in FLAT.list():
      if D['title'] == FLAT.title(n):
        return n

    new_note = FLAT.make_new(title=D['title'])
    with open(FLAT.to_path(new_note)) as f:
      content = f.read()
    with open(FLAT.to_path(new_note), "w") as f:
      f.write(f"# {D['month']} {D['day_of_month']}\n\n{content}Tags: Journal\n")
    return new_note

  @classmethod
  def append_to_note(_, note, content):
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
      f.write(content)
      f.write("".join(lines[metadata_linenum:]))


  @classmethod
  def handle_msg(_, note, form):

    # debug
    print(note, ',' + repr(form))

    # ignore empty messages
    if '' == form['msg']:
      return

    msg = "- msg: " + form['msg'] + "\n  - Date: " + util.get_current_time() + "\n"

    FLAT.append_to_note(note, msg)

  @classmethod
  def handle_edit(_, note, form):

    # read note
    with open(FLAT.to_path(note), "w") as f:
      f.write(form['text'])
# END FLAT

class FLAT_PARSER:

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

# END FLAT_PARSER

class FLAT_RENDER:
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
    # TODO fix the style for this localhost business
    emacs_buttons = ""
    if 'localhost' in request.headers['Host']:
      emacs_buttons = (
        f'<form method="post">'
        f'<button name="edit" value="{note}">edit</button>'
        f'<button name="open" value="{note}">open</button>'
        f'</form>'
        f'<button onclick="copy()">copy uuid</button>'
        f'<script>function copy() {{ navigator.clipboard.writeText("{note}"); }}</script>'
      )

    navbar = RENDER.nav(*extras, emacs_buttons)
    return "".join(navbar)

  @classmethod
  def NOTE(R, note):
    content = util.read_file(FLAT.to_path(note))

    # parse references and links in file
    content = FLAT_PARSER.parse(content)

    forward_links = R._section_forward_links(note)
    backlinks = R._section_backward_links(note)

    bar = R._bar(note,
                 f'<a href="/disc/{note}">disc</a>',
                 f'<a href="/edit/{note}">edit</a>',
                 )

    # compose html
    title = FLAT.title(note)
    result = "".join([f"<!DOCTYPE hmtl><html><head>{RENDER.STYLE()}<title>{title}</title></head>",
                      f"<body>{bar}<div class=\"content\"><pre style='font-feature-settings: \"liga\" 0'>",
                      f'<h1 class="title">{title}</h1>',
                      f"{content}{forward_links}{backlinks}</pre></div></body></html>"])
    return Response(result, mimetype="text/html")

  @classmethod
  def INDEX(R):
    note = FLAT.get_index()

    content = util.read_file(FLAT.to_path(note))

    # parse references and links in file
    content = FLAT_PARSER.parse(content)

    bar = R._bar(note,
                 f'<a href="/disc/{note}">disc</a>',
                 f'<a href="/edit/{note}">edit</a>',
                 )

    # compose html
    title = FLAT.title(note)
    result = "".join([f"<!DOCTYPE hmtl><html><head>{RENDER.STYLE()}<title>{title}</title></head>",
                      f"<body>{bar}<div class=\"content\"><pre style='font-feature-settings: \"liga\" 0'>",
                      f'<h1 class="title">{title}</h1>',
                      f"{content}</pre>",
                      f"</div></body></html>"])
    return Response(result, mimetype="text/html")

  @classmethod
  def LIST(R, items, title, linkfunc, colsfunc=lambda x: tuple(), namefunc=lambda x: x):
    """
    @param colsfunc - returns content for the other columns in this item's row in a list
    """
    header = f"<!DOCTYPE html><html><head>{RENDER.STYLE()}<title>{title}</title></head><body><div class=\"content\">"
    body = """<table style="table-layout: fixed; width: 100%">"""
    for i in items:
      td_style = '"text-overflow: ellipsis; white-space: nowrap; overflow: hidden;"'
      columns = "".join(map(lambda x: f"<td style={td_style}>" + x + "</td>", colsfunc(i)))
      body += f'<tr><td style={td_style}><a href="{linkfunc(i)}">{namefunc(i)}</a></td>{columns}</li>'
    body += "</ul>"
    footer = "</div></body></html>"
    return Response(header + body + footer, mimetype="text/html")

# END FLAT RENDER

@app.route("/all")
def get_all():
  return FLAT_RENDER.LIST(FLAT.list(), title="Notes", linkfunc=FLAT.to_url,
                     colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                     namefunc=FLAT.title)

@app.route("/recents")
def recents():
  return FLAT_RENDER.LIST(reversed(util.sort_recent(files=FLAT.list(),
                                        root_path=FLAT.path)),
                     title="Recent Notes",
                     linkfunc=FLAT.to_url,
                     colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                     namefunc=FLAT.title)

@app.route("/creation")
def creation():
  """returns a list of notes by creation date"""
  return FLAT_RENDER.LIST(reversed(FLAT.list_by_create_date()),
                     title="Recent Notes",
                     linkfunc=FLAT.to_url,
                     colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                     namefunc=FLAT.title)


@app.route("/tag/<tag>")
def tag(tag):
  return FLAT_RENDER.LIST(reversed([x for x in FLAT.list_by_create_date() if 'Tags' in FLAT.metadata(x) and tag in set(FLAT.metadata(x)['Tags'].split())]),
                     title="Tag: " + tag,
                     linkfunc=FLAT.to_url,
                     colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                     namefunc=FLAT.title)


@app.route("/note/<note>", methods=['GET', 'POST'])
def get_note(note):

  if not note.endswith(".note"): # /note/UUID.disc -> /disc/UUID.note
    return redirect("/" + note[-4:] + "/" + note[:-5] + ".note")

  # handle emacs section of bar, which is in both discussion and note
  if request.method == 'POST':
    if 'open' in request.form:
      FLAT.open(request.form['open'])
      return Response('', 204)
    if 'edit' in request.form:
      FLAT.edit(request.form['edit'])
      return Response('', 204)

    print("ERROR: unhandled POST request with form:")
    pprint(request.form)
    return Response('', 500)

  # default case: handle rendering
  return FLAT_RENDER.NOTE(note)

@app.route("/index.html")
def to_root():
  return redirect("/", code=302)

@app.route("/", methods=["GET", "POST"])
def get_root():
  if 'content' in request.form and \
      len(note_title := request.form['content'].strip()) != 0:
    return redirect("/edit/" + FLAT.make_new(title=note_title), code=302)

  return FLAT_RENDER.INDEX()
