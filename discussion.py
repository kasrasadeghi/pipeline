import os

class DISCUSSION_RENDER:
  @classmethod
  def MSG(cls, msg, timerender=None):
    try:
      msg_date = msg['children'][0]['value'].split('Date: ', 1)[1]
      msg_content = msg["value"].split("msg: ", 1)[1]
      origin = msg.get('origin', None)  # second argument of .get() is a default value

      if timerender:
        date = timerender(msg_date)
      else:
        date = util.date_cmd("-d", msg_date, "+%b %d %T")
      return (
        (f'<a href="/disc/{origin}">' if origin else "") +
        f'<div class="msg">'
        f'<div class="msg_timestamp">{date}</div>'
        f'<div class="msg_content">{escape(msg_content)}</div>'
        f'</div>' +
        (f'</a>' if origin else "")
      )
    except:
      print("ERROR: could not render msg: '" + str(msg) + "'")
      return str(msg)

  @classmethod
  def MAIN(cls, note):
    sections = PARSER.parse_file(FLAT.to_path(note))

    acc = []
    for section in sections:
      if section['section'] != 'entry':
        acc.append(f'<pre>--- {section["section"]} --- </pre>')

      pre_acc = list()

      # don't print two empty blocks consecutively
      for block in PARSER.trim_newlines(section['blocks']):

        if block == ['']:
          debug("whitespace")
          pre_acc.append('')
          continue

        for item in block:
          # if item is a tree/node
          if isinstance(item, dict):
            if 0 != len(pre_acc):
              acc.append("<pre>" + '\n'.join(pre_acc) + "</pre>")
              pre_acc = list()

            result = RENDER.node(item)
            if result:
              acc.append(result)
              continue

          if isinstance(item, str):
            pre_acc.append(item)
            debug("string:", item)
            continue

          acc.append(repr(item))

      if 0 != len(pre_acc):
        acc.append("<pre>" + '\n'.join(pre_acc) + "</pre>")
        pre_acc = list()

    content = '\n'.join(acc)

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
                      f'<form method="post"><input class="msg_input" autocomplete="off" autofocus type="text" name="msg"></form>',
                      f"</div></body></html>"])
    return Response(result, mimetype="text/html")


@app.route("/disc/<note>", methods=["GET", "POST"])
def get_disc(note):
  # handle messages
  if request.method == 'POST':
    if COMMAND.PARSE(note, request.form['msg']):
      FLAT.handle_msg(note, request.form)
    return redirect(f"/disc/{note}", code=302)

  # default case: handle rendering
  return DISCUSSION_RENDER.MAIN(note)
