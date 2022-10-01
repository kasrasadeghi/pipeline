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
    return TREE.is_singleton(block) and DISCUSSION.is_msg(block[0])

  @staticmethod
  def date(msg):
    return msg['children'][0]['value'].removeprefix('Date: ')
# end DISCUSSION


class DISCUSSION_RENDER:
  @staticmethod
  def MAIN(note):
    content = RENDER.page(note, PARSER.parse_file(FLAT.to_path(note)))

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
  def msg(msg, **kwargs):
    timerender = kwargs.get('timerender', None)

    # try:
    msg_date = DISCUSSION.date(msg)
    msg_content = RENDER.line(msg["value"].removeprefix("msg: "), **kwargs)

    if timerender:
      date = timerender(msg_date)
    else:
      date = util.date_cmd("-d", msg_date, "+%T")

    return (
      f'<div id="{msg_date}" class="msg">'
      f'<div class="msg_timestamp">{date}</div>'
      f'<div class="msg_content">{msg_content}</div>'
      f'</div>'
    )
    # except Exception as e:
      # LOG({"ERROR while rendering msg": msg, "exception": e})
      # raise e
      # return str(msg)

  @staticmethod
  def section(section, **kwargs):
    current_day = None

    def render_msg(msg):
      nonlocal current_day
      day_of_msg = util.date_cmd("-d", DISCUSSION.date(msg), "+%b %d %Y")

      result = DISCUSSION_RENDER.msg(msg, timerender=lambda x: util.date_cmd("-d", x, "+%T"), **kwargs)

      # when we detect a new day, prepend a day banner
      if current_day != day_of_msg:
        current_day = day_of_msg
        result = RENDER_UTIL.banner(current_day) + result

      return result

    acc = list()
    acc.append(f'<pre>--- {section["section"]} --- </pre>')
    # don't print two empty blocks consecutively
    for block in TREE.blocks_from_section(section):
      acc.append(RENDER.block(block, render_msg=render_msg, **kwargs))

    return '\n'.join(acc)

# end DISCUSSION_RENDER


@app.route("/disc/<note>", methods=["GET", "POST"])
def get_disc(note):
  DEBUG.init_state()

  # handle messages
  if request.method == 'POST':
    unhandled, result_url = COMMAND.PARSE(note, request.form['msg'])
    LOG({'unhandled': unhandled, 'result_url': result_url, 'commands': COMMAND.handlers})
    if unhandled:
      FLAT.handle_msg(note, request.form)
    if result_url:
      return redirect(result_url)
    return redirect(FLAT.to_url(note, view='disc'))

  # default case: handle rendering
  return DISCUSSION_RENDER.MAIN(note)
