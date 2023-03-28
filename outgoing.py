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
      case {'link': str() as link, 'linktype': 'root-link'}:
        # remarkable note link
        return
      case {'link': ParseResult() as url, 'linktype': 'internal-link'}:
        if hasattr(self, 'curr_msg') and \
           url.fragment and \
           FLAT.exists(url.path.removeprefix('/disc/')):
          if self.only_cross_note and self.curr_note == url.path.removeprefix('/disc/'):
            return
          self.result.append({'msg': self.curr_msg, 'target': {'note': url.path.removeprefix('/disc/'), 'date': unquote_plus(url.fragment)}})
        return
      case _:
        raise NotImplementedError(lc)

  def line(self, line):
    assert isinstance(line, list)
    for line_content in line:
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
        self.line(line['line'])
    else:
      for node in block:
        self.node(node)

  def msg(self, msg):
    # {msg,date,content}
    self.curr_msg = msg
    for line_content in msg['msg']:
      self.line_content(line_content)
    del self.curr_msg

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

  def __init__(self, note, only_cross_note=True):
    self.only_cross_note = only_cross_note
    if isinstance(note, dict) and note.keys() == {'note', 'rewrite'}:
      self.curr_note = note['note']
      self.result = list()
      self.page(note['rewrite'])
    else:
      self.curr_note = note
      self.result = list()
      page = REWRITE.note(note)
      self.page(page)


def tagwrap(tag, o):
  return f'<{tag}>{o}</{tag}>'

@app.route('/api/outgoing/<note>')
def get_outgoing(note):
  o = Outgoing(note)
  result = "\n".join(map(lambda p: str(p[0]) + '\n -> ' + str(p[1]), o.result))
  return tagwrap('pre', result)

@app.route('/api/graph/inout')
def get_inout():
  result = list()
  inout = GRAPH.collect_inout()
  from itertools import chain
  result.append(f"{len(inout)} notes with {len(list(chain(*map(lambda v: v['outgoing'], inout.values()))))} references\n")
  for i, (note, data) in enumerate(inout.items()):
    if len(data['outgoing']) > 0 or 'incoming' in data:
      # result.append(f"{i:4} note '{FLAT.title(note)}'\n")
      result.append(f"\n<span style='color: purple'>{i:4} note '{FLAT.title(note)}'</span>\n")
    # else:

    if len(data['outgoing']) > 0:
      result.append('  outgoing:')
      for out in data['outgoing']:
        result.append(DISCUSSION_RENDER.msg(out['msg'], origin_note=note))
        result.append(FLASK_UTIL.ESCAPE(f"      -> {FLAT.title(out['target']['note'])} @ {out['target']['date']}\n"))

    if 'incoming' in data:
      result.append('  incoming:')
      for incoming in data['incoming']:
        result.append(DISCUSSION_RENDER.msg(incoming['msg'], origin_note=incoming['source-note']))
        result.append(FLASK_UTIL.ESCAPE(f"      <- {FLAT.title(incoming['source-note'])} @ {incoming['msg']['date']}\n"))

  result = ''.join(result)
  return tagwrap('style', '.msg { display: flex; }\n .msg_timestamp {margin-right: 1em;} ') + tagwrap('pre', result)
