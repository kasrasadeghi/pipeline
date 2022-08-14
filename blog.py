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
      if not TREE.is_singleton(b):
        ABORT("ERROR: parsing blog post")
      blog_post = b[0]
      LOG(blog_post)
      post = NODE.splay(blog_post, ['note'])
      post.internal_name = blog_post['value']

      yield post

  @staticmethod
  def parse_postlist():
    lines = FLAT.read_note(BLOG.postlist)

    node = PARSER.parse_content("".join(lines))

    if node[0]['section'] != "entry":
      ABORT(f"ERROR: parsing entry section from node: {TREE.dump_tree(node)}")

    blocks = list(filter(lambda x: not TREE.is_newline(x), node[0]['blocks']))
    LOG(blocks)

    for b in blocks:
      if not TREE.is_singleton(b):
        ABORT(f"ERROR while parsing blog post: block '{b}' is not a singleton")
      blog_post = b[0]
      LOG(blog_post)
      post = NODE.splay(blog_post, ['title', 'filename', 'note'])
      post.internal_name = blog_post['value']

      yield post

  @staticmethod
  def try_note_to_post(note):
    for post in BLOG.parse_postlist():
      if post.note == note:
        return post
    ABORT(f"ERROR: post for note '{note}' not found")

  @staticmethod
  def post(post):
    return f'<a href="blog/posts/{post.filename}">{post.title}</a>'

  @staticmethod
  def bar():
    note = BLOG.root
    return FLAT_RENDER._bar(
      note,
      f'<a href="/note/{note}">note</a>'
      f'<a href="/edit/{note}">edit</a>'
    )

  @staticmethod
  def RENDER():
    bar = BLOG.bar()

    try:
      acc = []
      for post_slug in BLOG.parse_root():
        blog_post = BLOG.try_note_to_post(post_slug.note)
        acc.append("<li>" + BLOG.post(blog_post) + "</li>")
      content = "<ul>blog post list:" + "\n".join(acc) + "</ul>"

      title = BLOG.title()
    except Boundary as e:
      LOG(str(e))
      return FLAT_RENDER.NOTE(BLOG.root)

    # compose html
    return f"""
      <!DOCTYPE html>
      <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>{title}</title>
        </head>
        <body>
          {content}
        </body>
      </html>"""


@app.route("/blog")
def get_blog():
  DEBUG.init_state()
  return BLOG.RENDER()


@COMMAND.REGISTER('BLOG')
def COMMAND_BLOG(args, handle_msg):
  arg = args['arg'].strip()

  try:
    match arg:
      case "COMPILE":
        acc = []
        for post in BLOG.parse_postlist():
          cmd = f"python parser.py {FLAT.to_path(post.note)} | tee posts/{post.filename}"
          util.cmd(cmd, shell=True, cwd=BLOG.distpath)
          acc.append(cmd + "\n")
        pass
        # TODO compile root page as index.html
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
    DEBUG.CATCH(e)
    _, note_referer = FLASK_UTIL.REFERER_NOTE()
    return redirect(note_referer)
