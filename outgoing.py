class Outgoing:
  def line_content(self, lc):
    from urllib.parse import unquote_plus, urlunparse, ParseResult
    match lc:
      case str():
        return
      case {'tag': tag}:
        return
      case {'cmd': cmd}:
        return
      case {'link': str() as link, 'linktype': 'simple-link'}:
        return
      case {'link': str() as note, 'linktype': 'note'}:
        return
      case {'link': ParseResult() as url, 'linktype': 'internal-link'}:
        if hasattr(self, 'msg') and \
           url.fragment and \
           FLAT.exists(url.path.removeprefix('/disc/')):
          self.result.append((self.msg, {'note': url.path.removeprefix('/disc/'), 'date': unquote_plus(url.fragment)}))
        return
      case _:
        raise NotImplementedError(lc)

  def line(self, line):
    for line_content in line['line']:
      self.line_content(line_content)

  def node(self, node):
    assert node.keys() == {'indent', 'value', 'children', 'line'}
    self.line(node['line'])
    for child in node['children']:
      self.node(child)

  def block(self, block):
    if isinstance(block, dict) and {'msg', 'date', 'content'} == block.keys():
      self.msg(block)
      return

    if block == ['']:
      return

    assert len(block) > 0
    if block[0].keys() == {'line'}:
      for line in block:
        self.line(line)
    else:
      for node in block:
        self.node(node)

  def msg(self, msg):
    # {msg,date,content}
    self.msg = msg
    for line_content in msg['msg']:
      self.line_content(line_content)
    del self.msg

  def root(self, root):
    for block in root['children']:
      self.block(block)

  def section(self,section):
    # CONSIDER maybe handling lines
    # if 'lines' in section:
    #   section['lines']

    if 'blocks' in section:
      for block in section['blocks']:
        self.block(block)

    elif 'roots' in section:
      for root in section['roots']:
        self.root(root)


  def page(self, page):
    for section in page:
      self.section(section)

  def __init__(self, note):
    self.note = note
    self.result = list()
    page = REWRITE.note(note)
    self.page(page)


@app.route('/api/outgoing/<note>')
def get_outgoing(note):
  o = Outgoing(note)
  result = "\n".join(map(lambda p: str(p[0]) + '\n -> ' + str(p[1]), o.result))
  return f'<pre>{result}</pre>'
