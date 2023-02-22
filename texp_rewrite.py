class TEXP_REWRITE:
  @staticmethod
  def block_is_msg(T):
    return T.value == 'msg' and T[0].value == 'content' and T[1].value == 'date'

  @staticmethod
  def is_newline(T):
    return T.value == 'block' and len(T) == 1 and T[0].value == 'line' and len(T[0]) == 1 and T[0][0] == ''

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
    if DISCUSSION.block_is_msg(block):
      return Texp('msg',
                  Texp('content', *TEXP_REWRITE.line(DISCUSSION.msg_content(block[0]))),
                  Texp('date', DISCUSSION.date(block[0])))
    return Texp('block', *block)

  @staticmethod
  def section(section):
    """ transform: section -> block """
    acc_blocks = list()
    prev_is_msg = False
    for block in section['blocks']:
      block = TEXP_REWRITE.block(block)
      if prev_is_msg and TEXP_REWRITE.is_newline(block):
        continue
      prev_is_msg = TEXP_REWRITE.block_is_msg(block)
      acc_blocks.append(block)
    return Texp('section', section['title'], Texp('blocks', *acc_blocks))

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
  dump = result.format('page', 'section', 'blocks', 'block', 'msg')
  # dump = result.dump()
  # dump = FLASK_UTIL.ESCAPE(dump)
  return '<pre>' + str(len(dump)) + dump + "</pre>"
