# tree shaping utilities

class TREE:
  @staticmethod
  def filesize(note):
    return f"<pre><br/>(file size: {os.path.getsize(FLAT.to_path(note))} bytes)</pre>"

  @staticmethod
  def blocks_from_section(section):
    return TREE.squash_messages(TREE.trim_newlines(section['blocks']))

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
          and DISCUSSION.is_msg(blocks[i-1][0])

        before_msg = (i+1) < len(blocks) \
          and TREE.is_singleton(blocks[i+1]) \
          and DISCUSSION.is_msg(blocks[i+1][0])

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
          acc.append(FLASK_UTIL.ESCAPE(B))
        else:
          debug('huh', B, debugmode='ACTIVE')
          acc.append('[')
          for EL in B:
            acc.append(' ' + FLASK_UTIL.ESCAPE(EL))
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
