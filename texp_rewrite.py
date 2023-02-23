class TEXP_REWRITE:
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
  def tree(tree):
    """ rewrite: block -> (| message block)"""
    if (x := tree.match("(tree (node (indent 0) (value {content}) (children (node (indent 1) (value {date}) children)))))"))[0]:
      msg = x[1]
      msg.value = 'msg'
      return msg
    return tree

  @staticmethod
  def section(section):
    """ transform (traverse & rewrite): section -> section """

    # do the traverse
    acc = Texp('trees')
    for tree in section['trees']:
      acc.push(TEXP_REWRITE.tree(tree))

    # remove newlines if they're after msgs
    prev_is_msg = None
    new_acc = Texp('trees')
    for tree in acc:
      if tree.match('(newline)')[0] and prev_is_msg:
        prev_is_msg = tree.value == 'msg'
        continue
      prev_is_msg = tree.value == 'msg'
      new_acc.push(tree)

    return Texp('section', section['title'], new_acc)

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
