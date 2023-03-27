class DUMP:
  @staticmethod
  def node(node):
    raise NotImplementedError(node)

  @staticmethod
  def block(block):
    raise NotImplementedError(block)

  @staticmethod
  def line_content(lc):
    match lc:
      case str():
        return lc
      case {'tag': tag}:
        return tag
      case {'link': link, 'linktype': _}:
        return ': ' + link
      case _:
        raise NotImplementedError(lc)

  @staticmethod
  def line(line):
    return ''.join(map(DUMP.line_content, line['line']))

  @staticmethod
  def msg(msg):
    return '- ' + msg['content'] + "\n  - Date: " + msg['date'] + '\n\n'

  @staticmethod
  def root(root):
    acc = list()
    # acc.append(str(root))
    for child in root['children']:
      if isinstance(child, dict) and {'msg', 'date', 'content'} == child.keys():
        acc.append(DUMP.msg(child))
      else:
        if child == ['']:
          acc.append('\n')
          continue
        for node in child:
          elif node.keys() == {'line'}:
            acc.append(DUMP.line(node))
    return '\n'.join(acc)

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

    return '\n'.join(acc)

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
