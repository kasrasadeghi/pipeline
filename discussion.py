class DISCUSSION:

  @staticmethod
  def is_msg(item):
    """ checks whether an item in a block is a msg """
    if not isinstance(item, dict):
      LOG("ERROR: cannot check a non-dictionary:", item)
      return False
    return item['value'].startswith('msg: ')

  @staticmethod
  def block_is_msg(block):
    """
    checks whether the block is just one msg
    - this is the most common case
    """
    # TODO consider choosing between:
    # - only singleton message blocks, where we'd only use block_is_msg
    # - multimessage blocks, where we could have multiple messages in a block, possible useful for quotes and includes
    return TREE.is_singleton(block) and DISCUSSIOn.is_msg(block[0])
# end DISCUSSION


class DISCUSSION_RENDER:
  @staticmethod
  def MAIN(note):
    content = TREE.page(note, PARSER.parse_file(FLAT.to_path(note)))

    bar = FLAT_RENDER._bar(note,
                           f'<a href="/note/{note}">note</a>'
                           f'<a href="/edit/{note}">edit</a>'
                           )

    # compose html
    title = FLAT.title(note)
    result = (
      f"<div class=\"msgbox\" style='font-feature-settings: \"liga\" 0'>"
      f"{content}</div>"
      f'<form method="post"><input class="msg_input" autocomplete="off" autofocus type="text" name="msg"></form>'
    )
    return RENDER.base_page(DICT(title, bar, content=result))

  @staticmethod
  def msg_content(content):

    # cont is continuation
    # base is the escape function for when we have no more rendering left to do
    def parse_url(S, cont, base):
      if ': ' in content:
        prefix, potentially_url = S.rsplit(': ', 1)

        if potentially_url.strip().startswith('https://'):
          return cont(prefix, base) + ": " + TREE.link(potentially_url)

        if potentially_url.strip().endswith(".note") and \
           len('f177969a-aa24-410d-970d-93cd1fc09678.note') == len(potentially_url.strip()):
          return cont(prefix, base) + ": " + TREE.note(potentially_url)

      return cont(S, base)

    def highlight_tags(S, base):
      # replace DAILY with linked DAILY and run base() on everything between
      return "<a href='/daily'><b>DAILY</b></a>".join(map(base, S.split("DAILY")))

    basic_escape = lambda x: str(escape(x))

    return parse_url(content, cont=highlight_tags, base=basic_escape)

  @staticmethod
  def msg(msg, timerender=None):
    try:
      msg_date = msg['children'][0]['value'].removeprefix('Date: ')
      origin = msg.get('origin', None)  # second argument of .get() is a default value
      msg_content = DISCUSSION_RENDER.msg_content(msg["value"].removeprefix("msg: "))

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
      LOG("ERROR: could not render msg: '" + str(msg) + "'")
      LOG("exception: str(e)")
      return str(msg)


# end DISCUSSION_RENDER


@app.route("/disc/<note>", methods=["GET", "POST"])
def get_disc(note):
  DEBUG.init_state()

  # handle messages
  if request.method == 'POST':
    if COMMAND.PARSE(note, request.form['msg']):
      FLAT.handle_msg(note, request.form)
    return redirect(f"/disc/{note}")

  # default case: handle rendering
  return DISCUSSION_RENDER.MAIN(note)
