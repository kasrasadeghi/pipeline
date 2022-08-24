# tree renderer, not to be confused with the general purpose rendering utils in render.py

class TREE:
  @staticmethod
  def link(url):
    return f'<a href="{url}">{url}</a>'

  @staticmethod
  def note(note):
    return f'<a href="{FLAT.to_url(note, view="disc")}">{note}</a>'

  @staticmethod
  def node(item, **kwargs):
    render_msg = kwargs.get('render_msg', None)
    result = None

    level = item['indent']
    if level == -1:  # toplevel
      indent = ""
    elif level == 0:
      indent = "- "
    else:
      indent = (level * "  ") + "- "

    if DISCUSSION.is_msg(item):
      if render_msg:
        return render_msg(item)
      else:
        return DISCUSSION_RENDER.msg(item)

    if item['value'].startswith('link: '):
      url = item['value'].removeprefix('link: ')
      result = f'<pre>{indent}link: {TREE.link(url)}</pre>'
      debug("link:", repr(item), debugmode='RENDER LINK')

    if item['value'].startswith('note: '):
      note = item['value'].removeprefix('note: ').strip()
      result = f"<pre>{indent}note: {TREE.note(note)}</pre>"

    if None == result:
      debug('item, but none matched:', repr(item), debugmode='RENDER')
      result = "<pre>" + indent + str(escape(item['value'])) \
        + (": " if item['children'] and not item['value'].strip().endswith(':') else "") \
        + "</pre>"

    acc = list()
    acc.append(result)

    for child in item['children']:
      acc.append(TREE.node(child))

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
  def filesize(note):
    return f"<pre><br/>(file size: {os.path.getsize(FLAT.to_path(note))} bytes)</pre>"

  @staticmethod
  def blocks_from_section(section):
    return TREE.squash_messages(TREE.trim_newlines(section['blocks']))

  @staticmethod
  def section(section):
    acc = list()
    if section['section'] != 'entry':
      acc.append(f'<pre>--- {section["section"]} --- </pre>')

    if section['section'] == 'DISCUSSION':
      return DISCUSSION_RENDER.section(section)

    if section['section'] == 'METADATA':
      if JOURNAL.is_journal(section):
        return JOURNAL_RENDER.METADATA(TREE.parse_metadata(section))

    # don't print two empty blocks consecutively
    for block in TREE.blocks_from_section(section):

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
  def page(note, sections):
    return '\n'.join(map(TREE.section, sections)) + TREE.filesize(note)

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
