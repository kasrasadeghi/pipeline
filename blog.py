class BLOG:
  root = "37a95556-2ec0-4f0d-b6af-d3dd263d4763.note"

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
  def parse():
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
      internal_name = blog_post['value']
      title, filename, note = [c['value'] for c in blog_post['children']]
      title = title.removeprefix("title: ")
      filename = "blog/posts/" + filename.removeprefix("filename: ")
      note = note.removeprefix("note: ")

      yield DICT(internal_name, title, filename, note)

  @staticmethod
  def post(post):
    return f'<a href="{post.filename}">{post.title}</a>'

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
      for blog_post in BLOG.parse():
        acc.append("<li>" + BLOG.post(blog_post) + "</li>")
      content = "<ul>blog post list:" + "\n".join(acc) + "</ul>"

      title = BLOG.title()
    except Boundary as e:
      content = "couldn't parse blog list:\n" + DEBUG.CATCH(e)
      title = "Kaz Blog"

    # compose html

    result = (
      f"<div class=\"msgbox\" style='font-feature-settings: \"liga\" 0'>"
      f"{content}</div>"
      f'<form method="post"><input class="msg_input" autocomplete="off" autofocus type="text" name="msg"></form>'
    )
    return RENDER.base_page(DICT(title, content, bar))


@app.route("/blog")
def get_blog():
  DEBUG.init_state()
  return BLOG.RENDER()
