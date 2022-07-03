class PLAN:
  pass

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

      print(block)

      if "DAILY" in block[0]['value']:
        msg_blocks.append(block)

    result = list()
    for b in msg_blocks:
      result.append(TREE.msg(b[0], lambda x: util.date_cmd("-d", x, "+%T")))
    return "".join(result)


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
                      f"</div></body></html>"])
    return Response(result, mimetype="text/html")


@app.route('/plan/<note>')
def get_plan_note(note):
  return PLAN_RENDER.MAIN(note)
