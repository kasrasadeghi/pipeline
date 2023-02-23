class TEXP_REWRITE:
  context = dict()

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
      msg = Texp('msg')
      msg.value = 'msg'
      msg.push(Texp('content', x[1].get('content').removeprefix('msg: ')))
      msg.push(Texp('Date', x[1].get('date').removeprefix('Date: ')))
      return msg
    return tree

  @staticmethod
  def discussion_section(section):
    disc_section = section.get('title') == 'DISCUSSION'
    journal_disc_section = (
      section.get('title') == 'entry' and
      'note' in TEXP_REWRITE.context and
      'Tags' in FLAT.metadata(TEXP_REWRITE.context['note']) and
      'Journal' in FLAT.metadata(TEXP_REWRITE.context['note'])['Tags']
    )

    if not (disc_section or journal_disc_section):
      return section

    # handle discussion sections
    roots = Texp('roots', Texp('pre_roots'))

    for tree in section['trees']:
      match tree:
        case Texp(value='msg') as msg:
          if msg.get('content').startswith("- "):
            roots[-1].push(msg)
          else:  # new root
            roots.push(Texp('root', msg))

        case _:
          roots[-1].push(tree)

    if roots:
      roots[-1].value = 'root_final'

    return Texp('section', section['title'], roots)


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

    result = TEXP_REWRITE.discussion_section(Texp('section', section['title'], new_acc))

    return result

  @staticmethod
  def page(page):
    """ traverse: page -> section """
    acc = list()
    for section in page:
      acc.append(TEXP_REWRITE.section(section))
    return Texp('page', *acc)

  @staticmethod
  def note(note):
    page = PARSER.parse_file(FLAT.to_path(note))
    TEXP_REWRITE.context['note'] = note
    result = TEXP_REWRITE.page(page)
    TEXP_REWRITE.context = dict()
    return result

@app.route('/api/texp/<note>')
def get_texp(note):
  result = TEXP_REWRITE.note(note)
  # dump = page.format('page', 'section', 'blocks', 'trees', 'msg', 'block', 'tree')
  dump = result.format('page', 'section', 'blocks', 'trees', 'block', 'tree', 'root', 'roots', 'msg')
  # dump = FLASK_UTIL.ESCAPE(dump)
  return '<pre>' + str(len(dump)) + dump + "</pre>"
