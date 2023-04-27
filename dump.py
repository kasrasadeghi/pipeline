class DUMP:
  @staticmethod
  def line_content(lc):
    from urllib.parse import urlunparse, ParseResult
    match lc:
      case str():
        return lc
      case {'tag': tag}:
        return tag
      case {'cmd': cmd}:
        return cmd
      case {'link': str() as link, 'linktype': 'simple-link'}:
        return link
      case {'link': str() as note, 'linktype': 'note'}:
        return note
      case {'link': ParseResult() as parsed_url, 'linktype': _}:
        return ': ' + urlunparse(parsed_url)
      case _:
        raise NotImplementedError(lc)

  @staticmethod
  def line(line):
    return ''.join(map(DUMP.line_content, line['line']))

  @staticmethod
  def node(node):
    assert node.keys() == {'indent', 'value', 'children', 'line'}
    indent = RENDER.indent(node)
    return indent + node['value'] + '\n' + ''.join(map(DUMP.node, node['children']))

  @staticmethod
  def block(block):
    if isinstance(block, dict) and {'msg', 'date', 'content'} == block.keys():
      return DUMP.msg(block)

    if block == []:
      return '\n'

    assert len(block) > 0
    if block[0].keys() == {'line'}:
      return '\n'.join(map(DUMP.line, block))
    else:
      return ''.join(map(DUMP.node, block))

  @staticmethod
  def msg(msg):
    return '- ' + msg['content'] + "\n  - Date: " + msg['date'] + '\n\n'

  @staticmethod
  def root(root):
    acc = list()
    for block in root['children']:
      acc.append(DUMP.block(block))
    return ''.join(acc)

  @staticmethod
  def section(section):
    if 'lines' in section:
      assert section['title'] == 'METADATA', section
      return '--- METADATA --- \n' + '\n'.join(section['lines'])

    acc = list()
    if section['title'] != 'entry':
      acc.append('--- ' + section['title'] + ' ---')
    if 'blocks' in section:
      for block in section['blocks']:
        acc.append(DUMP.block(block))

    elif 'roots' in section:
      for root in section['roots']:
        acc.append(DUMP.root(root))

    return ''.join(acc)

  @staticmethod
  def page(page):
    return '\n'.join(DUMP.section(section) for section in page)

  @staticmethod
  def note(note):
    page = REWRITE.note(note)
    return DUMP.page(page)

@app.route('/api/dump/<note>')
def get_dump(note):
  result = DUMP.note(note)
  return f'<pre>{result}</pre>'
