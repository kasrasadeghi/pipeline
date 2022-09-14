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

    LOG('call forward link')
    forward_links = FLAT_RENDER._section_forward_links(note)

    # compose html
    title = FLAT.title(note)
    result = (
      f"<div class=\"msgbox\" style='font-feature-settings: \"liga\" 0'>"
      f"{content}<pre>{forward_links}</pre></div>"
      f'<form method="post"><input class="msg_input" autocomplete="off" autofocus type="text" name="msg"></form>'
    )
    return RENDER.base_page(DICT(title, bar, content=result))

  @staticmethod
  def msg_content(content, **kwargs):

    # cont is continuation
    # base is the escape function for when we have no more rendering left to do
    def parse_url(S, cont, base):
      nonlocal kwargs

      if ': ' in content:
        prefix, potentially_url = S.rsplit(': ', 1)

        if potentially_url.strip().startswith('https://'):
          return cont(prefix, base) + ": " + RENDER.link(potentially_url, **kwargs)

        if potentially_url.strip().endswith(".note") and \
           len('f177969a-aa24-410d-970d-93cd1fc09678.note') == len(potentially_url.strip()):
          LOG({'note in message': potentially_url, 'msg': content})
          return cont(prefix, base) + ": " + RENDER.note(potentially_url, **kwargs)

      return cont(S, base)

    def highlight_tags(S, base):
      # replace DAILY with linked DAILY and run base() on everything between
      return "<a href='/daily'><b>DAILY</b></a>".join(map(base, S.split("DAILY")))

    basic_escape = lambda x: str(escape(x))

    return parse_url(content, cont=highlight_tags, base=basic_escape)

  @staticmethod
  def msg(msg, **kwargs):
    timerender = kwargs.get('timerender', None)

    try:
      msg_date = DISCUSSION.date(msg)
      msg_content = DISCUSSION_RENDER.msg_content(msg["value"].removeprefix("msg: "), **kwargs)

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
    except Exception as e:
      import inspect
      LOG({"ERROR while rendering msg": msg, "exception": e})
      return str(msg)

  @staticmethod
  def section(section, **kwargs):
    current_day = None

    def render_msg(msg):
      nonlocal current_day
      day_of_msg = util.date_cmd("-d", DISCUSSION.date(msg), "+%b %d %Y")

      result = DISCUSSION_RENDER.msg(item, timerender=lambda x: util.date_cmd("-d", x, "+%T"), **kwargs)

      # when we detect a new day, prepend a day banner
      if current_day != day_of_msg:
        current_day = day_of_msg
        result = RENDER_UTIL.banner(current_day) + result

      return result

    acc = list()
    acc.append(f'<pre>--- {section["section"]} --- </pre>')
    # don't print two empty blocks consecutively
    for block in TREE.blocks_from_section(section):
      if block == ['']:
        acc.append('<br/>')
        continue

      for item in block:
        # if item is a tree/node
        if isinstance(item, dict):
          acc.append(RENDER.node(item, render_msg=render_msg, **kwargs))
          continue

        if isinstance(item, str):
          acc.append(f"<pre>{item}</pre>")
          continue

        acc.append(repr(item))

    return '\n'.join(acc)

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
