class TEXP_REWRITE:

  @staticmethod
  def is_newline(T):
    return T.match('(newline)')

  @staticmethod
  def line(line):
    def parse_url(S):

      if ': ' not in S:
        return [S]
      else:
        prefix, url = S.rsplit(': ', 1)
        prefix = prefix + ': '
        url = url.strip()

        if url.startswith('https://'):
          url = Texp('link', url)

        elif url.endswith(".note") and \
           FLAT.note_id_len() == len(url):
          url = Texp('note', url)

        elif url.startswith('/'):
          url = Texp('internal-link', url)

        elif url.startswith(FLASK_UTIL.URL_ROOT()):
          from urllib.parse import unquote_plus
          url = Texp('url-internal-link', unquote_plus(url))

        return [prefix, url]

    return parse_url(line)

  @staticmethod
  def block(block):
    """ rewrite: block -> (| message block)"""
    match block:
      case Texp(value='block', children=[
        Texp(value='node', children=[
          Texp(value='indent', children=[0]),
          Texp(value='value', children=[msg_content]),
          Texp(value='children', children=[
            Texp(value='node', children=[
              Texp(value='indent', children=[1]),
              Texp(value='value', children=[date]),
              Texp(value='children', children=[])
            ])
          ])
        ])
      ]):
        if msg_content.startswith('msg: ') and date.startswith('Date: '):
          return Texp('msg', Texp('content', msg_content), Texp('date', date))
      case Texp(value='block', children=[
        Texp(value='node', children=children) as node
      ]):
        return node
    return block

  @staticmethod
  def section(section):
    """ transform: section -> block """
    acc = Texp('trees')
    prev_is_msg = False
    for block in section['trees']:
      block = TEXP_REWRITE.block(block)
      if prev_is_msg and TEXP_REWRITE.is_newline(block):
        continue
      prev_is_msg = DISCUSSION.is_msg(block)
      acc.push(block)
    return Texp('section', section['title'], acc)

  @staticmethod
  def page(page):
    """ traverse: page -> section """
    acc = list()
    for section in page:
      acc.append(TEXP_REWRITE.section(section))
    return Texp('page', *acc)

@app.route('/api/texp/<note>')
def get_texp(note):
  page = PARSER.parse_file(FLAT.to_path(note))
  result = TEXP_REWRITE.page(page)
  # dump = page.format('page', 'section', 'blocks', 'trees', 'msg', 'block', 'tree')
  dump = result.format('page', 'section', 'blocks', 'trees', 'msg', 'block', 'tree')
  # dump = FLASK_UTIL.ESCAPE(dump)
  return '<pre>' + str(len(dump)) + dump + "</pre>"
