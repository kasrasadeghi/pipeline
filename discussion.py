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
    if not 'children' in msg:
      LOG({'ERROR': msg})
    if isinstance(msg, list):
      LOG({'ERROR': 'msg cannot be list, you\'re probably passing in a block', 'msg': msg})
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
  def msg_content(msg):
    return msg["value"].removeprefix("msg: ")

  @staticmethod
  def msg(msg, **kwargs):
    timerender = kwargs.get('timerender', None)

    # try:
    msg_date = DISCUSSION.date(msg)
    msg_content = RENDER.line(DISCUSSION_RENDER.msg_content(msg), **kwargs)

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
    def render_msg(msg):
      return DISCUSSION_RENDER.msg(msg, timerender=lambda x: util.date_cmd("-d", x, "+%T"), **kwargs)

    # a day has roots, each of which has content (the first message) and children (what is collapsed)

    pre_day_acc = list()
    days = list()
    current_day = None
    current_root = None

    for block in TREE.blocks_from_section(section):
      LOG(block)
      if not DISCUSSION.block_is_msg(block):
        # handle regular blocks that are not messages
        if len(days) == 0:
          pre_day_acc.append(block)
          continue

        if len(days[-1].roots) == 0:
          days[-1].pre_roots.append(block)
          continue

        days[-1].roots[-1].children.append(block)
        continue

      # we're handling a message
      msg = block[0]

      day_of_msg = util.date_cmd("-d", DISCUSSION.date(msg), "+%b %d %Y")
      # we found a new day
      if current_day != day_of_msg:
        days.append(DICT(day=day_of_msg, pre_roots=list(), roots=list()))
        current_day = day_of_msg

      # we found a new root
      if len(days[-1].roots) == 0 or not msg['value'].startswith('msg: - '):
        days[-1].roots.append(DICT(content=block, children=list(), final=False))
        current_root = days[-1].roots[-1]
        continue

      days[-1].roots[-1].children.append(block)

    if current_root is not None:
      current_root.final = True

    acc = list()

    def render_block(block):
      nonlocal render_msg
      x = RENDER.block(block, render_msg=render_msg, **kwargs)
      LOG({'render block': block, 'result': x})
      # return "<pre>" + str(block) + "\n</pre>"
      return x

    # don't print two empty blocks consecutively
    for day in days:
      acc.append(RENDER_UTIL.banner(day.day))
      for root in day.roots:
        if root.children:
          if root.final:
            acc.append("<details open><summary>")
          else:
            acc.append("<details><summary>")
          acc.append(render_block(root.content))
          acc.append("</summary>")
          for block in root.children:
            acc.append(render_block(block))
          acc.append("</details>")
        else:
          acc.append(render_block(root.content))

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
