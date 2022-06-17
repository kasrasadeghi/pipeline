class DISCUSSION_PARSER:
  @classmethod
  def MAIN(cls, content):
    lines = content.splitlines()
    acc = list()

    parse_msg = False
    msg = ""
    tmp_acc = list()

    for L in lines:

      if (result := FLAT_PARSER.parse_ref(L))[0]:
        tmp_acc.append(result[1])
        continue

      if (result := FLAT_PARSER.parse_link(L))[0]:
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


class DISCUSSION_RENDER:
  @classmethod
  def MSG(cls, msg):
    try:
      msg_date = msg['children'][0]['value'].split('Date: ', 1)[1]
      msg_content = msg["value"].split("msg: ", 1)[1]
      origin = msg.get('origin', None)  # second argument of .get() is a default value
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
    content = util.read_file(FLAT.to_path(note))
    content = DISCUSSION_PARSER.MAIN(content)

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
