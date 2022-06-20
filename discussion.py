import os

class DISCUSSION_RENDER:
  @classmethod
  def MSG(cls, msg, timerender=None):
    try:
      msg_date = msg['children'][0]['value'].removeprefix('Date: ')
      msg_content = msg["value"].removeprefix("msg: ")
      msg_content_altered = False
      origin = msg.get('origin', None)  # second argument of .get() is a default value

      if ': ' in msg_content:
        prefix, potentially_url = msg_content.rsplit(': ', 1)
        if potentially_url.strip().startswith('https://'):
          msg_content = prefix + ": " + TREE.link(potentially_url)
          msg_content_altered = True
        if potentially_url.strip().endswith(".note") and \
           len('f177969a-aa24-410d-970d-93cd1fc09678.note') == len(potentially_url.strip()):
          msg_content = prefix + ": " + TREE.note(potentially_url)
          msg_content_altered = True

      if not msg_content_altered:
        msg_content = escape(msg_content)

      if timerender:
        date = timerender(msg_date)
      else:
        date = util.date_cmd("-d", msg_date, "+%b %d %T")
      return (
        (f'<a href="/disc/{origin}">' if origin else "") +
        f'<div class="msg">'
        f'<div class="msg_timestamp">{date}</div>'
        f'<div class="msg_content">{msg_content}</div>'
        f'</div>' +
        (f'</a>' if origin else "")
      )
    except Exception as e:
      print("ERROR: could not render msg: '" + str(msg) + "'")
      print(" ", str(e))
      return str(msg)

  @classmethod
  def MAIN(cls, note):
    content = TREE.page(PARSER.parse_file(FLAT.to_path(note)))

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
