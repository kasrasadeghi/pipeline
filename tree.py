# tree renderer, not to be confused with the general purpose rendering utils in render.py

class TREE:
  @staticmethod
  def link(url):
    return f'<a href="{url}">{url}</a>'

  @staticmethod
  def note(note):
    return f'<a href="{FLAT.to_url(note, view="disc")}">{note}</a>'

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
      msg_content = TREE.msg_content(msg["value"].removeprefix("msg: "))

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

  @staticmethod
  def is_msg(item):
    """ checks whether an item in a block is a msg """
    if not isinstance(item, dict):
      print("ERROR: cannot check a non-dictionary:", item)
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
    return TREE.is_singleton(block) and TREE.is_msg(block[0])

  @staticmethod
  def node(item, level=0):
    result = None

    indent = ("  " * (level - 1)) + ("- " if level > 0 else "")

    if TREE.is_msg(item):
      result = TREE.msg(item, lambda x: util.date_cmd("-d", x, "+%T"))
      return result

    if item['value'].startswith('link: '):
      url = item['value'].removeprefix('link: ')
      result = '<pre>' + indent + 'link: ' + TREE.link(url) + "</pre>"
      debug("link:", repr(item), debugmode='RENDER LINK')

    if item['value'].startswith('note: '):
      result = f"<pre>{indent}{item['value']}</pre>"

    if None == result:
      debug('item, but none matched:', repr(item), debugmode='RENDER')
      result = "<pre>" + indent + str(escape(item['value'])) \
        + (": " if item['children'] and not item['value'].strip().endswith(':') else "") \
        + "</pre>"

    acc = list()
    acc.append(result)

    for child in item['children']:
      acc.append(TREE.node(child, 1 + level))

    return "".join(acc)

  @staticmethod
  def parse_metadata(section):
    metadata_section = "\n".join(map(
      lambda x: "\n".join(x),
      section['blocks']))
    metadata = {p[0]: p[1].strip() for p in
                [x.split(":", 1) for x in metadata_section.split('\n') if x]}
    return metadata

  @staticmethod
  def section(section):
    acc = list()
    if section['section'] != 'entry':
      acc.append(f'<pre>--- {section["section"]} --- </pre>')

    if section['section'] == 'METADATA':
      if JOURNAL.is_journal(section):
        return JOURNAL_RENDER.METADATA(TREE.parse_metadata(section))

    # don't print two empty blocks consecutively
    for block in TREE.squash_messages(TREE.trim_newlines(section['blocks'])):

      if block == ['']:
        debug("whitespace")
        acc.append('<br/>')
        continue

      for item in block:
        # if item is a tree/node
        if isinstance(item, dict):

          acc.append(TREE.node(item))
          continue

        if isinstance(item, str):
          acc.append(f"<pre>{item}</pre>")
          debug("string:", item)
          continue

        acc.append(repr(item))

    return '\n'.join(acc)

  @staticmethod
  def page(sections):

    acc = list()
    for section in sections:
      acc.append(TREE.section(section))

    return '\n'.join(acc)

  @staticmethod
  def is_newline(block):
    """ a newline block looks like this: [''] """
    return len(block) == 1 and block[0] == ''

  @staticmethod
  def is_singleton(block):
    """ a singleton is a block with one item that is a dict, and thus a parsed tree """
    return len(block) == 1 and isinstance(block[0], dict)

  @staticmethod
  def trim_newlines(section):
    """ this function deletes consecutive newline blocks """
    new_section = []

    i = 0
    while i < len(section):
      block = section[i]
      new_section.append(block)
      debug("trim newlines", repr(block), TREE.is_newline(block))

      if i < len(section) and TREE.is_newline(section[i]):
        while i < len(section) and TREE.is_newline(section[i]):
          i += 1
          debug("trim newlines, consuming:", repr(block))
      else:
        i += 1

      if i < len(section):
        debug("next section:", section[i])

    return new_section

  @staticmethod
  def squash_messages(blocks):
    """ removes newline blocks between messages """
    new_blocks = list()

    i = 0
    while i < len(blocks):
      if TREE.is_newline(blocks[i]):
        after_msg = (i-1) >= 0 \
          and TREE.is_singleton(blocks[i-1]) \
          and TREE.is_msg(blocks[i-1][0])

        before_msg = (i+1) < len(blocks) \
          and TREE.is_singleton(blocks[i+1]) \
          and TREE.is_msg(blocks[i+1][0])

        if after_msg and before_msg:
          i += 1
          continue

      new_blocks.append(blocks[i])
      i += 1

    return new_blocks

  @staticmethod
  def dump_tree(page):
    acc = list()
    for S in page:
      acc.append(S['section'])
      for B in S['blocks']:
        if len(B) == 1:
          acc.append(str(escape(B)))
        else:
          debug('huh', B, debugmode='ACTIVE')
          acc.append('[')
          for EL in B:
            acc.append(' ' + str(escape(EL)))
          acc.append(']')
    return "\n".join(acc)

@app.route('/render/trim_newline/<note>')
def test_render_trim_newline(note):

  page = PARSER.parse_file(FLAT.to_path(note))

  new_page = list()
  for S in page:
    new_S = dict()
    new_S['section'] = S['section']
    new_S['blocks'] = TREE.trim_newlines(S['blocks'])
    new_page.append(new_S)

  return DEBUG.TEXT('test_parse', TREE.dump_tree(new_page))

@app.route('/render/trim_and_squash/<note>')
def test_render_trim_and_squash(note):

  page = PARSER.parse_file(FLAT.to_path(note))

  new_page = list()
  for S in page:
    new_S = dict()
    new_S['section'] = S['section']
    new_S['blocks'] = TREE.squash_messages(TREE.trim_newlines(S['blocks']))
    new_page.append(new_S)

  return DEBUG.TEXT('test_parse', TREE.dump_tree(new_page))
