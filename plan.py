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

      dangling_done = list()
      for d in done:
        task = d.block[0]['value'].removeprefix("msg: DAILY DONE:")
        corresponding_todo_msg = "msg: DAILY ADD:" + task

        found = False
        for t in todo:
          if corresponding_todo_msg == t.block[0]['value']:
            found = True
            t.isDone = True
            d.startedWhen = t.block[0]['children'][0]

        if not found:
          dangling_done.append(d)
      return (
        "<pre>TODO:</pre>"
        + "".join(map(lambda x: render_msg(x.block),
                      filter(lambda y: not y.isDone, todo)))
        + "<pre>DONE:</pre>"
        + "".join(map(lambda x: render_msg(x.block), done))
        + ("<pre>DANGLING DONE:</pre>"
           + "".join(map(lambda x: render_msg(x.block), dangling_done)) if dangling_done else "")
      )


    except Exception as e:
      DEBUG.CATCH(e)
      return "<pre>error parsing message:\n</pre>" + "".join(map(render_msg, msg_blocks))



  @staticmethod
  def page(sections):
    acc = list()
    for section in sections:
      acc.append(PLAN_RENDER.section(section))

    return '\n'.join(acc)

  @staticmethod
  def MAIN(note):
    content = PLAN_RENDER.page(PARSER.parse_file(FLAT.to_path(note)))

    bar = FLAT_RENDER._bar(note,
                           f'<a href="/note/{note}">note</a>'
                           f'<a href="/edit/{note}">edit</a>'
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


@app.route('/plan/<note>')
def get_plan_note(note):
  init_state()
  return PLAN_RENDER.MAIN(note)
