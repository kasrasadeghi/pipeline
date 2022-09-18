class FLAT:
  path = "/home/kasra/notes"

  @staticmethod
  def cmd(*args, **kwargs):
    if 'cwd' not in kwargs:
      kwargs['cwd'] = FLAT.path
    return util.cmd(*args, **kwargs)

  @classmethod
  def list(cls):
    return [x for x in os.listdir(cls.path) if cls.exists(x) and not (x[0] == '#' and x[-1] == '#')]

  @classmethod
  def listabs(cls):
    return list(map(lambda x: cls.path + "/" + x, cls.list()))

  @classmethod
  def to_url(_, note, view="note"):
    return f"/{view}/{note}"

  @classmethod
  def to_path(cls, note):
    return cls.path + "/" + note

  @staticmethod
  def find_note_with_title(title):
    for n in FLAT.list():
      if title == FLAT.title(n):
        return n
    return None

  @staticmethod
  def open_note(note):
    return open(FLAT.to_path(note))

  @staticmethod
  def read_note(note):
    with FLAT.open_note(note) as N:
      return N.read()

  @staticmethod
  def note_read_lines(note):
    with FLAT.open_note(note) as N:
      # for some reason, "f.readlines()" and "for L in f:" don't usually do what
      # i expect so i'm using splitlines().  I think splitlines handles weird
      # cases with empty last lines and empty front matter correctly, actually
      # preserving them instead of randomly chopping them off
      lines = N.read().splitlines()
    return lines

  @staticmethod
  def try_from_url(url):
    host = FLASK_UTIL.HOST()
    if url.startswith(f"http://{host}"):
      url = url.removeprefix(f"http://{host}")

    for view in ["note", "disc", "plan", "daily", "edit"]:
      if url.startswith(f'/{view}/'):
        return view, url.removeprefix(f"/{view}/")

    return None, url

  @classmethod
  def exists(cls, note):
    return os.path.isfile(cls.to_path(note))

  @classmethod
  def get_index(cls):
    return "4e0ce4ff-1663-49f9-8ced-30f91202ae08.note"  # hardcoded value, CONSIDER looking for "index" in Tags

  @classmethod
  def init_note(cls, note, title):
    with open(cls.to_path(note), "w+") as f:
      f.write("--- METADATA ---\n")
      f.write("Date: ")
      f.write(util.get_current_time())
      f.write(f"Title: {title}\n")

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
      raise FileNotFoundError(f"metadata does not exist for note '{note}'")

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
      if 0 == len(acc):
        ABORT(f"did not find metadata for note '{note}'")

    result = {p[0]: p[1].strip() for p in [x.split(":", 1) for x in acc]}
    return result

  @staticmethod
  def metadata_section(section):
    metadata_section = "\n".join(map(
      lambda x: "\n".join(x),
      section['blocks']))
    metadata = {p[0]: p[1].strip() for p in
                [x.split(":", 1) for x in metadata_section.split('\n') if x]}
    return metadata

  @classmethod
  def title(cls, note):
    return cls.metadata(note)['Title']

  @classmethod
  def list_by_create_date(cls):
    return sorted(cls.list(), key=lambda n: util.parse_time_to_utc(FLAT.metadata(n)['Date']))

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
    LOG(note + ': ' + repr(form))

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
    LOG('forward link section')
    forward_link_list = GRAPH.collect_refs(note)
    if 0 != len(forward_link_list):
      return "\n\n--- LINKS ---\n" + "\n".join([R._render_link(L) for L in forward_link_list])
    else:
      return ""

  @classmethod
  def _section_backward_links(R, note):
    backlink_map = GRAPH.backlinks_refmap()[0]
    if note in backlink_map:
      return "\n\n--- BACKLINKS ---\n" + "\n".join([R._render_link(L) for L in backlink_map[note]])
    else:
      return ""

  @classmethod
  def _bar(R, note, *extras):
    navbar = RENDER_UTIL.nav(*extras)
    return "".join(navbar)

  @classmethod
  def NOTE(R, note):
    content = util.read_file(FLAT.to_path(note))

    # parse references and links in file
    content = FLAT_PARSER.parse(content)

    forward_links = R._section_forward_links(note)
    # backlinks = R._section_backward_links(note)

    bar = R._bar(note,
                 f'<a href="/disc/{note}">disc</a>',
                 f'<a href="/edit/{note}">edit</a>',
                 )

    # compose html
    title = FLAT.title(note)
    result = (f"<pre style='font-feature-settings: \"liga\" 0'>"
              f"{content}{forward_links}"
              # f"{backlinks}"
              "</pre>")
    return RENDER.base_page(DICT(title, bar, content=result))

  @classmethod
  def INDEX(R):
    note = FLAT.get_index()

    content = util.read_file(FLAT.to_path(note))
    lines_of_code = util.cmd("tokei", shell=True, cwd="/home/kasra/projects/notes-website")

    # parse references and links in file
    content = FLAT_PARSER.parse(content)

    bar = R._bar(note,
                 f'<a href="/note/{note}">note</a>',
                 f'<a href="/disc/{note}">disc</a>',
                 f'<a href="/edit/{note}">edit</a>',
                 )

    # compose html
    title = FLAT.title(note)
    result = (f"<pre style='font-feature-settings: \"liga\" 0'>"
              f"{content}\n{lines_of_code}</pre>")
    return RENDER.base_page(DICT(title, bar, content=result))

  @classmethod
  def LIST(R, items, title, linkfunc, colsfunc=lambda x: tuple(), namefunc=lambda x: x):
    """
    @param colsfunc - returns content for the other columns in this item's row in a list
    """
    content = """<table style="table-layout: fixed; width: 100%">"""
    for i in items:
      td_style = '"text-overflow: ellipsis; white-space: nowrap; overflow: hidden;"'
      columns = "".join(map(lambda x: f"<td style={td_style}>" + x + "</td>", colsfunc(i)))
      content += f'\n<tr><td style={td_style}><a href="{linkfunc(i)}">{namefunc(i)}</a></td>{columns}</li></tr>'
    content += "\n</table>"
    return RENDER.base_page(DICT(title, content, bar=None))

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
                     linkfunc=lambda x: FLAT.to_url(x, view='disc'),
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
