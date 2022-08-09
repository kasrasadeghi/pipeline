# DEPENDS ON journal.py

class PLAN_RENDER:
  @staticmethod
  def section(section):
    if section['section'] == 'METADATA':
      return TREE.section(section)

    if section['section'] != 'entry':
      return ''

    msg_blocks = list()
    for block in section['blocks']:
      if not TREE.block_is_msg(block):
        continue

      if "DAILY" in block[0]['value']:
        msg_blocks.append(block)

    def render_msg(msg_block, date_prefix=''):
      return TREE.msg(msg_block[0], lambda x: date_prefix + util.date_cmd("-d", x, "+%T"))

    try:
      import itertools  # repeat
      todo = [DICT(isDone=False, block=item)
              for item in filter(lambda x: "ADD" in x[0]['value'], msg_blocks)]
      done = [DICT(startedWhen=None, block=item)
              for item in filter(lambda x: "DONE" in x[0]['value'], msg_blocks)]
      rest = [DICT(startedWhen=None, block=item)
              for item in filter(lambda x: "DONE" not in x[0]['value'] and "ADD" not in x[0]['value'], msg_blocks)]

      dangling_done = list()
      for d in done:
        done_msg = d.block[0]['value'].removeprefix("msg: ")
        task = done_msg.split("DAILY DONE:", 1)[1]  # get what's after DAILY DONE:
        corresponding_todo_msg = "DAILY ADD:" + task

        found = False
        for t in todo:
          if corresponding_todo_msg in t.block[0]['value']:
            found = True
            t.isDone = True
            d.startedWhen = t.block[0]['children'][0]

        if not found:
          dangling_done.append(d)

      undone_todos = list(filter(lambda y: not y.isDone, todo))
      def render_todos(title, l):
        if l:
          return f"<pre>{title}:</pre>" + "".join(map(lambda x: render_msg(x.block), l))
        else:
          return ""

      return (render_todos("TODO", undone_todos)
              + render_todos("DONE", done)
              + render_todos("DANGLING DONE", dangling_done)
              + render_todos("MISC", rest))


    except Exception as e:
      DEBUG.CATCH(e)
      return "<pre>error parsing message:\n</pre>" + "".join(map(render_msg, msg_blocks))



  @staticmethod
  def page(note, sections):
    acc = list()
    for section in sections:
      acc.append(PLAN_RENDER.section(section))

    return '\n'.join(acc) + TREE.filesize(note)

  @staticmethod
  def MAIN(note):
    content = PLAN_RENDER.page(note, PARSER.parse_file(FLAT.to_path(note)))

    bar = FLAT_RENDER._bar(note,
                           f'<a href="/disc/{note}">disc</a>'
                           )

    # compose html
    title = FLAT.title(note)
    result = "".join([f"<!DOCTYPE hmtl><html><head>{RENDER.STYLE()}<title>{title}</title></head>",
                      f"<body>{bar}<div class=\"content\">"
                      f"<div class=\"msgbox\" style='font-feature-settings: \"liga\" 0'>",
                      f'<h1 class="title">{title}</h1>',
                      f"{content}</div>",
                      "<br>", DEBUG.CONTENT(),
                      f"</div></body></html>"])
    return Response(result, mimetype="text/html")


@app.route('/daily', defaults={"note": None})
@app.route('/daily/<note>')
def get_plan_note(note):
  if not note:
    _, note = FLASK_UTIL.REFERER_NOTE()
    return redirect(FLAT.to_url(note, view='daily'))

  DEBUG.init_state()
  return PLAN_RENDER.MAIN(note)
