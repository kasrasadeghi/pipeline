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
    # ignore empty messages
    if '' == form['msg']:
      return

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

        # use `date` to translate to current timezone because datetime in python sucks at timezones
        date = util.date_cmd("-d", L.split("- Date: ")[1], "+%T")
        acc.append(f'<div class="msg"><div class="msg_timestamp">{date}</div><div class="msg_content">{escape(msg)}</div></div>')
        parse_msg = False
        msg = ""
        continue

      tmp_acc.append(L)

    if tmp_acc:
      acc.append("<pre>" + "\n".join(tmp_acc) + "</pre>")

    return "\n".join(acc)
# END FLAT_PARSER


class FLAT_RENDER:

  @classmethod
  def TEXT(R, title, content):
    return Response(f"<!DOCTYPE hmtl><html><head>{RENDER.STYLE()}<title>{title}</title></head>"
                    + f"<body><pre>{content}</pre></body></html>", mimetype="text/html")

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
    content = util.read_file(FLAT.to_path(note))

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
    result = "".join([f"<!DOCTYPE hmtl><html><head>{RENDER.STYLE()}<title>{title}</title></head>",
                      f"<body>{bar}<pre style='font-feature-settings: \"liga\" 0'>",
                      f'<h1 style="{title_style}">{title}</h1>',
                      f"{content}{forward_links}{backlinks}</pre></body></html>"])
    return Response(result, mimetype="text/html")

  @classmethod
  def INDEX(R):
    note = FLAT.get_index()

    content = util.read_file(FLAT.to_path(note))

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
    result = "".join([f"<!DOCTYPE hmtl><html><head>{RENDER.STYLE()}<title>{title}</title></head>",
                      f"<body>{bar}<pre style='font-feature-settings: \"liga\" 0'>",
                      f'<h1 style="{title_style}">{title}</h1>',
                      f"{content}</pre>",
                      f'<form><input style="width: 80%" type="text" name="title"><input type="submit" value="New Note"/></form>'
                      f"</body></html>"])
    return Response(result, mimetype="text/html")

  @classmethod
  def DISCUSSION(R, note):
    content = util.read_file(FLAT.to_path(note))
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
    result = "".join([f"<!DOCTYPE hmtl><html><head>{RENDER.STYLE()}<title>{title}</title></head>",
                      f"<body>{bar}<div class=\"msgbox\" style='font-feature-settings: \"liga\" 0'>",
                      f'<h1 style="{title_style}">{title}</h1>',
                      f"{content}</div>",
                      f'<form method="post"><input class="msg_input" autocomplete="off" autofocus type="text" name="msg"></form>',
                      f"</body></html>"])
    return Response(result, mimetype="text/html")

  @classmethod
  def EDIT(R, note):
    content = util.read_file(FLAT.to_path(note))

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
    result = "".join([f"<!DOCTYPE hmtl><html><head>{RENDER.STYLE()}<title>{title}</title></head>",
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
    header = f"<!DOCTYPE html><html><head>{RENDER.STYLE()}<title>{title}</title></head><body>"
    body = """<table style="table-layout: fixed; width: 100%">"""
    for i in items:
      td_style = '"text-overflow: ellipsis; white-space: nowrap; overflow: hidden;"'
      columns = "".join(map(lambda x: f"<td style={td_style}>" + x + "</td>", colsfunc(i)))
      body += f'<tr><td style={td_style}><a href="{linkfunc(i)}">{namefunc(i)}</a></td>{columns}</li>'
    body += "</ul>"
    footer = "</body></html>"
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

  # handle bar, which is in both discussion and note
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

@app.route("/disc/<note>", methods=["GET", "POST"])
def get_disc(note):
  # handle messages
  if request.method == 'POST':
    FLAT.handle_msg(note, request.form)
    return redirect(f"/disc/{note}", code=302)

  # default case: handle rendering
  return FLAT_RENDER.DISCUSSION(note)

@app.route("/edit/<note>", methods=['GET', 'POST'])
def route_edit(note):
  if request.method == 'POST':
    FLAT.handle_edit(note, request.form)
    return redirect(f"/edit/{note}", code=302)

  return FLAT_RENDER.EDIT(note)


@app.route("/index.html")
def to_root():
  return redirect("/", code=302)

@app.route("/")
def get_root():
  if 'title' in request.args and len(request.args['title'].strip()) != 0:
    return redirect(FLAT.to_url(FLAT.make_new(title=request.args['title'].strip())), code=302)

  return FLAT_RENDER.INDEX()