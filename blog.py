"""
has 2 special notes
the root/ blog index
the postlist

some posts may be on the postlist but not on the root, as they may not be
indexed, but i still may want to send the specific link to people
"""

class BLOG:
  root = "37a95556-2ec0-4f0d-b6af-d3dd263d4763.note"  # BLOG index
  postlist = "973393c0-b3c5-43c5-8e6b-2d41b00cb172.note"  # BLOG all post list
  distpath = "/home/kasra/blog"

  @staticmethod
  def cmd(cmd):
    return util.cmd(cmd, shell=True, cwd=BLOG.distpath)

  @staticmethod
  def title():
    lines = FLAT.note_read_lines(BLOG.root)

    if len(lines) == 0:
      ABORT(f"ERROR: blog root file is empty {BLOG.root}")

    # parse title
    first_line = lines[0]
    if not first_line.startswith("# "):
      ABORT(f"ERROR: parsing title on first line: '{lines[0]}'")
    title = first_line.removeprefix("# ")

    return title

  @staticmethod
  def parse_root():
    lines = FLAT.note_read_lines(BLOG.root)

    node = PARSER.parse_content("\n".join(lines[1:]))

    if node[0]['section'] != "entry":
      ABORT(f"ERROR: parsing entry section from node: {TREE.dump_tree(node)}")

    blocks = list(filter(lambda x: not TREE.is_newline(x), node[0]['blocks']))

    for b in blocks:
      if not TREE.is_line(b):
        ABORT(f"ERROR: block is not singleton '{b}'")
      blog_post = b[0]
      LOG(blog_post)
      post = dict()
      post['internal_name'], post['note'] = blog_post.rsplit(': ', 2)

      yield post

  @staticmethod
  def parse_postlist():
    lines = FLAT.read_note(BLOG.postlist)

    node = PARSER.parse_content("".join(lines))

    if node[0]['section'] != "entry":
      ABORT(f"ERROR: parsing entry section from node: {TREE.dump_tree(node)}")

    blocks = list(filter(lambda x: not TREE.is_newline(x), node[0]['blocks']))

    for b in blocks:
      if not TREE.is_singleton(b):
        ABORT(f"ERROR while parsing blog post: block '{b}' is not a singleton")
      blog_post = b[0]
      post = NODE.splay(blog_post, ['title', 'filename', 'note'])
      post['internal_name'] = blog_post['value']

      yield post

  @staticmethod
  def try_note_to_post(note):
    for post in BLOG.parse_postlist():
      if post['note'] == note:
        return post
    ABORT(f"ERROR: post for note '{note}' not found")

# end BLOG


class BLOG_RENDER:
  @staticmethod
  def link_to_post(post, view):
    # view is either "internal" or "blog"
    return f"""<a href="/{view}/posts/{post['filename']}">{post['title']}</a>"""

  @staticmethod
  def bar():
    note = BLOG.root
    return RENDER_UTIL.nav(f'<a href="/note/{note}">note</a>'
                           f'<a href="/edit/{note}">edit</a>')

  @staticmethod
  def ROOT_CONTENT(view):
    acc = []
    for post_slug in BLOG.parse_root():
      blog_post = BLOG.try_note_to_post(post_slug['note'])
      acc.append("<div class='block'>" + BLOG_RENDER.link_to_post(blog_post, view) + "</div>")
    content = '\n'.join(acc)
    return content

  @staticmethod
  def ROOT():
    bar = BLOG_RENDER.bar()

    try:
      content = BLOG_RENDER.ROOT_CONTENT("internal")
      title = BLOG.title()
    except Boundary as e:
      LOG(e)
      return FLAT_RENDER.NOTE(BLOG.root)

    return BLOG_COMPILE.base_page(title, content)

# end BLOG_RENDER


class BLOG_TREE:
  @staticmethod
  def content(note):
    return BLOG_TREE.page(note, PARSER.parse_file(FLAT.to_path(note), tree_parser=ADV_TREE_PARSER.process_block))

  @staticmethod
  def page(note, sections):
    return '\n'.join(map(BLOG_TREE.section, sections))

  @staticmethod
  def is_subheading(block):
    if all(isinstance(b, str) for b in  block)\
      and all(b.startswith(" " * 4) for b in block[:-1]) \
      and len(block) > 1 \
      and block[-1].startswith((" " * 4) + "-") \
      and all(x == "-" for x in block[-1].strip()):
        return True
    return False

  @staticmethod
  def subheading(block):
    return "<h3>" + block[0] + "</h3>"

  @staticmethod
  def is_heading(block):
    if all(isinstance(b, str) for b in block)\
      and all(b.startswith(" | ") for b in block[:-1]) \
      and len(block) > 1 \
      and block[-1].startswith((" +") + "-") \
      and all(x == "-" for x in block[-1].removeprefix(" +").strip()):
        return True
    return False

  @staticmethod
  def heading(block):
    return "<h3>" + " ".join(map(lambda x: x[3:], block[:-1])) + "</h3>"

  @staticmethod
  def linkify(s):
    if "https://" in s:
      index = s.index("https://")
      return s[:index] + f'<a href="{s[index:]}">' + s[index:]+ '</a>'
    return None

  @staticmethod
  def codify(s):
    LOG(s)
    if s[0] in {"$", '|', '+', '#'}:
      return '<pre class="code">' + s + "</pre>"

    return None

  @staticmethod
  def code_blockify(block):
    def line_check(L):
      return (len(L) >= 1 and L[0] in {'$', '|', '+', '#'})

    LOG(block)
    if not any('value' in l and line_check(l['value']) for l in block):
      return block

    result = list()
    prev = None  # invariant: only not None when startswith '$ ' or list of startswith '$ '
    for node in block:
      if prev:
        if line_check(node['value']):
          if isinstance(prev, list):
            prev.append(node)
          elif isinstance(prev, dict):
            prev = [prev, node]
          else:
            ABORT('node is neither list nor dict-item: ' + str(node))
        else: # not startwith $, so flush prev to result
          if isinstance(prev, list):
            result.append({'type': 'code block', 'content': prev})
          elif isinstance(prev, dict):
            result.append(prev)
          prev = None
      else: # not prev
        if line_check(node['value']):
          prev = node
        else:
          result.append(node)

    if prev:
      if isinstance(prev, list):
        result.append({'type': 'code block', 'content': prev})
      elif isinstance(prev, dict):
        result.append(prev)
      prev = None

    LOG({"result": result, "prev": prev})

    return result

  @staticmethod
  def node(item):
    result = None
    comment = "<!-- " + str(item) + "-->"

    if 'type' in item:
      if item['type'] == 'code block':
        return "<pre class='code'>" + "\n".join(map(lambda x: x['value'], item['content'])) + "</pre>"
      else:
        ABORT('unknown item type' + str(item))

    assert('value' in item)

    is_codify = False

    if item['value'].startswith('note: '):
      note = item['value'].removeprefix('note: ').strip()
      result = f"<pre style='color: red'>{indent}note: {TREE.note(note)}</pre>"

    if None == result:
      result = BLOG_TREE.linkify(item['value'])

    if None == result:
      result = BLOG_TREE.codify(item['value'])
      if result:
        is_codify = True

    if None == result:
      result = item['value']

    if item['value'].startswith('- '):
      result = "<ul><li class='dash'>" + result.removeprefix('- ')

    if not is_codify:
      result += "<br/>"

    if 'children' in item and len(item['children']) != 0:
      header_acc = list()
      acc = list()

      children = item['children']
      child_iter = iter(children)

      if children[0]['indent'] > item['indent'] + 1:
        for child in child_iter:
          # if we see something at just +1, it's not the header's child, it's just a regular child.
          if child['indent'] == item['indent'] + 1:
            break
          header_acc.append(BLOG_TREE.node(child))

      for child in child_iter:
        child_result = BLOG_TREE.node(child)
        if child['indent'] == item['indent'] + 1\
           and not child['value'].startswith('- ')\
           and not item['value'].startswith('- '):
          acc.append("<ul>" + child_result + "</ul>")
        else:
          acc.append(child_result)

      header_children = '' if len(header_acc) == 0 else "\n<ul class='trailing_header'>" + '\n'.join(header_acc) + "</ul>"

      result= f"{result}{header_children}{''.join(acc)}\n"


    if item['value'].startswith('- '):
      result += "</li></ul>"

    return comment + result + "\n"

  @staticmethod
  def block(block):
    if BLOG_TREE.is_heading(block):
      return BLOG_TREE.heading(block)

    if BLOG_TREE.is_subheading(block):
      return BLOG_TREE.subheading(block)

    # before = block[:]  # debug
    block = BLOG_TREE.code_blockify(block)
    # LOG({"before": before, "block": block})  # debug

    acc = list()
    acc.append('<div class="kscroll block">')
    for item in block:
      # if item is a tree/node
      if isinstance(item, dict):
        acc.append(BLOG_TREE.node(item))
        continue

      if isinstance(item, str):
        acc.append(f"<pre style='color: red'>{item}</pre>")
        debug("string:", item)
        continue

      # acc.append(repr(item))

    acc.append('</div>')
    return "\n".join(acc)

  @staticmethod
  def section(section):
    if section['section'] != 'entry':
      return ''

    acc = list()
    for block in section['blocks']:
      if TREE.is_newline(block):
        acc.append('<br/>')
        continue

      acc.append(BLOG_TREE.block(block))

    return "\n".join(acc)

# end BLOG_TREE


class BLOG_COMPILE:
  @staticmethod
  def ROOT():
    try:
      content = BLOG_RENDER.ROOT_CONTENT("blog")
      title = BLOG.title()
    except Boundary as e:
      LOG(e)
      return ('internal server error', 404)

    return BLOG_COMPILE.base_page(title, content)

  @staticmethod
  def POST(post):
    note_content = PARSER.parse_file(FLAT.to_path(post.note))
    content = (BLOG_TREE.content(post.note) + \
               # "<pre>\n" + PRETTY.DUMP(note_content[0], no_symbol=True) + "</pre>"
               "")
    return BLOG_COMPILE.base_page(title=FLAT.title(post.note), content=content)

  @staticmethod
  def base_page(title, content):
    scroll = RENDER_UTIL.kscroll(
      foreground="#f88",
      background="#888"
    )

    return """
    <!DOCTYPE hmtl>
<html>
  <head>
     <meta name="viewport" content="initial-scale=1.0">
     <style>
       body { margin: 0.5% 0.5%; }
       .msgbox { margin: 0px;
             display: flex; flex-direction: column;
             align-content: stretch; align-items: flex-start; }
       pre { margin: 0px; }
       .msg { display: flex; margin: 3px; font-family: monospace; }
       .msg_timestamp { border-radius: 18px; color: rgb(230, 50, 120); }
       .msg_content { padding: 7px 12px 8px 12px; border-radius: 18px; background-color: rgb(0, 130, 250); color: rgb(250, 250, 250); overflow-wrap: anywhere;}

       """ + scroll + """

       .block { background: white; border: 2px solid grey; overflow-x: auto; padding: 2px; }
       body { background: rgb(56, 56, 65); }
       .content { max-width: 60em; margin: 0em auto; padding: 0em 1em; }

       pre.code { background: #ddd; min-width: min(60%, 400px); }

       ul { margin-block-start: 0px;
            padding-inline-start: 0.6em;
            margin-block-end: 0px;
          }

       body { font-size: 1.1em; }
       h1 { font-size: 1.15em; border-left: 2px white solid; }
       h2 { font-size: 1.12em; margin-left: 1em; }
       h3 { font-size: 1.12em; margin-left: 1em; }

       h1, h2, h3 {
           margin-left: 1em;
           padding: 0px 10px 6px 10px;
       }
       h1 { border-bottom: 2px white solid;
            color: white; }
       h2, h3 { border-bottom: 2px white solid;
                color: white; }
       h2, h3 {
           margin-right: 0;
           margin-bottom: 0;
           margin-top: 0;
       }

       code { font-family: "Noticia Text", serif;
              background: #ddd;
              padding: 2px 5px;
              margin-top: 2px;
            }

       /* string value for list-style-type:
          https://developer.mozilla.org/en-US/docs/Web/CSS/list-style-type */
       li { list-style-type: "  "; }
       li.dash { list-style-type: "- "; }

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
         .blogpara { font-family: monospace; background: red; }

         body { font-size: 0.9em; }

         h1 { font-size: 0.95em; border-left: 2px white solid; }
         h2 { font-size: 0.92em; margin-left: 1em; }
         h3 { font-size: 0.92em; margin-left: 1em; }
       }

       /* desktop */
       @media (min-aspect-ratio: 1/1) {
         .msg { flex-direction: row; align-items: baseline; }
         .msg_timestamp { margin: 0px 5px 0px 0px; }
       }
     </style>
     <title>
""" + title + """
     </title>
  </head>
  <body>
    <h1>
""" + title + """
    </h1>

    <div class='content'>""" + content + """</div>
  </body>
</html>
    """


@app.route("/blog")
def get_blog():
  return BLOG_COMPILE.ROOT()

@app.route("/internal")
def get_internal_blog():
  return BLOG_RENDER.ROOT()

@app.route("/blog/posts/<filename>")
@app.route("/internal/posts/<filename>", defaults={"blog_type": "internal"})
def get_internal_blog_post(filename, blog_type=None):
  def filename_to_post(url):
    for post in BLOG.parse_postlist():
      if post.filename == filename:
        return post
    ABORT(f"ERROR: post for url 'posts/{filename}' not found")

  post = filename_to_post(filename)

  if blog_type == "internal":
    return FLAT_RENDER.NOTE(post.note)
  else:
    return Response(BLOG_COMPILE.POST(post), 200, mimetype="text/html")


@app.route("/test/blog/<note>")
def test_blog_renderer(note):
  title = "testing blog render for '" + FLAT.title(note) + "'"
  content = BLOG_TREE.content(note)
  return BLOG_COMPILE.base_page(title, content)

@COMMAND.REGISTER('BLOG')
def COMMAND_BLOG(args, handle_msg, redirect_page):
  arg = args['arg'].strip()

  try:
    match arg:
      case "COMPILE":
        acc = []
        for post in BLOG.parse_postlist():
          with open(BLOG.distpath + "/posts/" + post.filename, "w+") as f:
            acc.append(f"compile ~/blog/posts/{post.filename}\n")
            f.write(BLOG_COMPILE.POST(post))
        pass

        # render root
        acc.append('compile root\n\n')
        with open(BLOG.distpath + "/index.html", "w+") as f:
          f.write(BLOG_COMPILE.ROOT())

        # TODO track changed files
        handle_msg("COMPILE")
        FLAT.append_to_note(args['origin'], "".join(acc))
      case "PUSH":
        handle_msg("PUSH")
        output = util.cmd(["make", "put"], cwd=BLOG.distpath)
        FLAT.append_to_note(args['origin'], output + "\n")
      case _:
        ABORT('unmatched command')

  except Exception as e:
    _, note_referer = FLASK_UTIL.REFERER_NOTE()
    return redirect(note_referer)
