class FLAT:
  path = os.path.join(os.path.expanduser('~'), "notes")

  # NOTE: configuration stuff is in this folder because it's in the ~/notes/ folder

  @staticmethod
  def default_config():
    return {
      "navbar_size": "40px",
      "header_color": "#bb6",
      "link_button_color": {"main": "orange", "hover": "red"},
      "msg_color": "#243d28",
      "nav_button_color": "#611",
      "base_text_color": "#ddd",
      "input_background_color": "#333",
      "body_background_color": "#222",
      "banner_color": "#aaa",
      "sidebar_animation_time": "0.1s",
      "desktopview_device_width_threshold": "1117px",
      "tag_style": "color: #000",
      "cmd_color": "#111",
      "msg_timestamp_color": "rgb(57, 146, 138)",
      "quote_timestamp_color": "rgb(240, 80, 160)",
    }

  @staticmethod
  def config_path():
    return FLAT.to_path('notes_config.json')

  @staticmethod
  def set_config(form):
    with open(FLAT.config_path(), "w") as f:
      f.write(form['text'])
      f.flush()

  @staticmethod
  def config():
    if not FLAT.exists('notes_config.json'):
      LOG("config doesn't exist")
      return FLAT.default_config()

    LOG("config exists")
    with open(os.path.join(FLAT.path, 'notes_config.json')) as f:
      # comment with '#'
      content = "\n".join(filter(lambda x: not x.strip().startswith('#'), f.read().split('\n')))
      try:
        return json.loads(content)
      except Exception as e:
        LOG('failed to read file, maybe invalid json?\n' + str(e) + "\n" + content)
        return FLAT.default_config()

  @staticmethod
  def note_id_len():
    return len("4e0ce4ff-1663-49f9-8ced-30f91202ae08.note")

  @staticmethod
  def cmd(args, **kwargs):
    if 'cwd' not in kwargs:
      kwargs['cwd'] = FLAT.path
    return util.cmd(*args, **kwargs)

  @classmethod
  def list(cls):
    return [x for x in os.listdir(cls.path) if x.endswith('.note') and not (x[0] == '#' and x[-1] == '#')]

  @staticmethod
  def list_by_mtime():
    return util.sort_mtime(FLAT.list(), cwd=FLAT.path)[::-1]

  @classmethod
  def listabs(cls):
    return list(map(lambda x: cls.path + "/" + x, cls.list()))

  @classmethod
  def to_url(_, note, view="note"):
    return f"/{view}/{note}"

  @classmethod
  def to_path(cls, note):
    return cls.path + "/" + note

  @classmethod
  def from_path(cls, path):
    return util.basename(path)

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
    # I think splitlines handles weird cases with empty last lines and empty
    # front matter correctly, actually preserving them instead of randomly
    # chopping them off
    return FLAT.read_note(note).split('\n')

  @staticmethod
  def try_from_url(url):
    if url.startswith(FLASK_UTIL.URL_ROOT()):
      url = url.removeprefix(FLASK_UTIL.URL_ROOT())

    for view in ["note", "disc", "plan", "daily", "edit"]:
      if url.startswith(f'{view}/'):
        return view, url.removeprefix(f"{view}/")

    return None, url

  @staticmethod
  def exists(note):
    return os.path.isfile(FLAT.to_path(note))

  @staticmethod
  def get_index():
    return "4e0ce4ff-1663-49f9-8ced-30f91202ae08.note"  # hardcoded value, CONSIDER looking for "index" in Tags

  @staticmethod
  def init_note(note, title):
    with open(FLAT.to_path(note), "w+") as f:
      f.write("--- METADATA ---\n"
              f"Date: {DATE.now()}\n"
              f"Title: {title}\n")
      f.flush()

  @staticmethod
  def make_new(title):
    with open("/proc/sys/kernel/random/uuid") as uuid:
      note = uuid.read().strip() + ".note"
    if FLAT.exists(FLAT.to_path(note)):
      return "/try-again"
    else:
      FLAT.init_note(note, title)
      return note

  @classmethod
  def metadata(cls, note):
    if note.startswith(cls.path):
      path = note
      note = FLAT.from_path(note)
    else:
      path = FLAT.to_path(note)
      note = note
    if not FLAT.exists(note):
      raise FileNotFoundError(f"cannot parse metadata for note '{note}'")

    lines = FLAT.note_read_lines(note)

    # find metadata
    metadata_linenum = -1
    for i, l in reversed(list(enumerate(lines))):
      if l == "--- METADATA ---":
        metadata_linenum = i
    assert metadata_linenum != -1, "couldnt find metadata in lines:\n" + "\n".join(lines)

    section = dict()
    section['lines'] = lines[metadata_linenum+1:]
    return FLAT.parse_metadata_from_section(section)

  @staticmethod
  def parse_metadata_from_section(section):
    acc = dict()
    for L in section['lines']:
      if L != '':
        key, value = L.split(":", 1)
        acc[key] = value.strip()
    return acc

  @staticmethod
  def title(note):
    return FLAT.metadata(note)['Title']

  @classmethod
  def list_by_create_date(cls):
    return sorted(cls.list(), key=lambda n: DATE.parse_time_to_utc(FLAT.metadata(n)['Date']))

  @classmethod
  def append_to_note(_, note, content):
    lines = FLAT.note_read_lines(note)

    # find metadata
    metadata_linenum = -1
    for i, l in reversed(list(enumerate(lines))):
      if l == "--- METADATA ---":
        metadata_linenum = i
    assert(metadata_linenum != -1)

    # write note with msg
    with open(FLAT.to_path(note), "w") as f:
      f.write("\n".join(lines[:metadata_linenum]) + "\n")
      f.write(content)
      f.write("\n".join(lines[metadata_linenum:]))
      f.flush()


  @classmethod
  def handle_msg(_, note, form):
    LOG(note + ': ' + repr(form))

    # ignore empty messages
    if '' == form['msg']:
      return

    msg = "- msg: " + form['msg'] + "\n  - Date: " + DATE.now() + "\n\n"

    FLAT.append_to_note(note, msg)

  @classmethod
  def handle_edit(_, note, form):
    with open(FLAT.to_path(note), "w") as f:
      f.write(form['text'])
      f.flush()
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

      acc.append(FLASK_UTIL.ESCAPE(L))

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
  def NOTE(R, note):
    content = util.read_file(FLAT.to_path(note))

    # parse references and links in file
    content = FLAT_PARSER.parse(content)

    forward_links = R._section_forward_links(note)
    # backlinks = R._section_backward_links(note)

    bar = RENDER_UTIL.nav(f'<a href="/disc/{note}">disc</a>',
                          f'<a href="/edit/{note}">edit</a>')

    # compose html
    title = FLAT.title(note)
    result = (f"<pre style='font-feature-settings: \"liga\" 0'>"
              f"{content}{forward_links}"
              # f"{backlinks}"
              "</pre>")
    return RENDER.base_page({'title': title, 'bar': bar, 'content': result})

  @classmethod
  def INDEX(R):
    note = FLAT.get_index()

    content = RENDER.content(note)

    bar = RENDER_UTIL.nav(f'<a href="/note/{note}">note</a>',
                          f'<a href="/disc/{note}">disc</a>',
                          f'<a href="/edit/{note}">edit</a>')

    # compose html
    title = FLAT.title(note)
    result = (f"<div class='msgbox'>"
              f"{content}\n</div>")
    return RENDER.base_page({'title': title, 'bar': bar, 'content': result})

  @classmethod
  def LIST(R, items, title,
           linkfunc=lambda x: FLAT.to_url(x, view='disc'),
           colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
           namefunc=FLAT.title):
    """
    @param colsfunc - returns content for the other columns in this item's row in a list
    """
    content = """<table style="table-layout: fixed; width: 100%">"""
    for i in items:
      td_style = '"text-overflow: ellipsis; white-space: nowrap; overflow: hidden;"'
      columns = "".join(map(lambda x: f"<td style={td_style}>" + x + "</td>", colsfunc(i)))
      content += f'\n<tr><td style={td_style}><a href="{linkfunc(i)}">{namefunc(i)}</a></td>{columns}</li></tr>'
    content += "\n</table>"
    return RENDER.base_page({"title": title, 'content': content})

# END FLAT RENDER

@app.route("/all")
def get_all():
  return FLAT_RENDER.LIST(FLAT.list(), title="Notes", linkfunc=FLAT.to_url,
                          colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                          namefunc=FLAT.title)

@app.route("/recents")
def recents():
  return FLAT_RENDER.LIST(FLAT.list_by_mtime(),
                          title="Recently Edited Notes")

@app.route("/creation")
def creation():
  """returns a list of notes by creation date"""
  return FLAT_RENDER.LIST(reversed(FLAT.list_by_create_date()),
                          title="Notes by Create Date")

@app.route("/tag/<tag>")
def tag(tag):
  return FLAT_RENDER.LIST(reversed([x for x in FLAT.list_by_create_date() if 'Tags' in FLAT.metadata(x) and tag in set(FLAT.metadata(x)['Tags'].split())]),
                          title="Tag: " + tag)


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
