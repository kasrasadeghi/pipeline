# tree renderer, not to be confused with the general purpose rendering utils in render.py

class TREE:
  @staticmethod
  def link(url):
    return f'<a href="{url}">{url}</a>'

  @staticmethod
  def note(note):
    return f'<a href="{FLAT.to_url(FLAT.to_disc(note))}">{note}</a>'

  @staticmethod
  def node(item, level=0):
    result = None

    indent = ("  " * (level - 1)) + ("- " if level > 0 else "")

    if item['value'].startswith('msg: '):
      result = DISCUSSION_RENDER.MSG(item, lambda x: util.date_cmd("-d", x, "+%T"))
      debug("msg:", repr(item))
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
  def page(sections):

    acc = []
    for section in sections:
      if section['section'] != 'entry':
        acc.append(f'<pre>--- {section["section"]} --- </pre>')

      pre_acc = list()

      # don't print two empty blocks consecutively
      for block in TREE.trim_newlines(section['blocks']):

        if block == ['']:
          debug("whitespace")
          acc.append('<br/>')
          continue

        for item in block:
          # if item is a tree/node
          if isinstance(item, dict):
            if 0 != len(pre_acc):
              acc.append("<pre>" + '\n'.join(pre_acc) + "</pre>")
              pre_acc = list()

            acc.append(TREE.node(item))
            continue

          if isinstance(item, str):
            pre_acc.append(item)
            debug("string:", item)
            continue

          acc.append(repr(item))

      if 0 != len(pre_acc):
        acc.append("<pre>" + '\n'.join(pre_acc) + "</pre>")
        pre_acc = list()

    return '\n'.join(acc)

  @staticmethod
  def trim_newlines(section):
    """
    this function deletes consecutive newline blocks
    - a newline block looks like this: ['']
    """
    new_section = []

    def is_newline(block):
      return len(block) == 1 and block[0] == ''

    i = 0
    while i < len(section):
      block = section[i]
      new_section.append(block)
      debug("trim newlines", repr(block), is_newline(block))

      if i < len(section) and is_newline(section[i]):
        while i < len(section) and is_newline(section[i]):
          i += 1
          debug("trim newlines, consuming:", repr(block))
      else:
        i += 1

      if i < len(section):
        debug("next section:", section[i])

    return new_section

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
    S['blocks'] = TREE.trim_newlines(S['blocks'])

  return DEBUG.TEXT('test_parse', TREE.dump_tree(new_page))
