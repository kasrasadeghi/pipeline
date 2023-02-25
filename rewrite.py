class REWRITE_RESULT:
  @staticmethod
  def block_is_msg(block):
    return isinstance(block, dict) and 'date' in block and 'msg' in block

class REWRITE:

  @staticmethod
  def line(line):
    def parse_url(S):
      if ': ' in S:
        prefix, url = S.rsplit(': ', 1)
        url = url.strip()

        if url.startswith('https://'):
          url = {'link': url}

        elif url.endswith(".note") and \
           FLAT.note_id_len() == len(url.strip()):
          url = {'note': url}

        elif url.startswith('/'):
          url = {'internal-link': url}

        elif url.startswith(FLASK_UTIL.URL_ROOT()):
          from urllib.parse import unquote_plus
          url = {'url-internal-link': unquote_plus(url)}
        return [prefix, ': ', url]

      return [S]

    return parse_url(line)

  @staticmethod
  def block(block):
    """ rewrite: block -> (| message block)"""
    match block:
      case [{ "value": content, "indent": 0, "children": [
              { "value": date, "indent": 1, "children": []}
           ]}]:
        if content.startswith('msg: ') and date.startswith('Date: '):  # i should actually have this be 'line':, not 'msg':.  maybe 'type' should be 'msg' or something.  maybe the id?
          return {'msg': REWRITE.line(content.removeprefix('msg: ')), 'content': content, 'date': date.removeprefix('Date: ')}
    return block

  @staticmethod
  def discussion_section(section):
    disc_section = section['title'] == 'DISCUSSION'
    journal_disc_section = (
      section['title'] == 'entry' and
      'note' in g.rewrite_note and
      'Tags' in FLAT.metadata(g.rewrite_note) and
      'Journal' in FLAT.metadata(g.rewrite_note)['Tags']
    )

    if not (disc_section or journal_disc_section):
      return section

    # handle discussion sections
    roots = [{'root': 'pre_roots', 'children': list()}]

    for block in section['blocks']:
      match block:
        case {'msg': _} as msg:
          if msg['msg'][0].startswith("- "):
            msg['msg'][0] = msg['msg'][0].removeprefix('- ')
            msg['content'] = msg['content'].removeprefix('- ')
            roots[-1]['children'].append(msg)
          else:  # new root
            roots.append({'root': 'nonfinal', 'children': [msg]})

        case _:
          roots[-1]['children'].append(block)

    if roots[-1]['root'] == 'nonfinal':
      roots[-1]['root'] = 'final'

    return section | {'roots': roots}

  @staticmethod
  def section(section):
    """ transform: section -> block """
    result = {'title': section['title'], 'lines': section['lines'], 'blocks': list()}
    prev_is_msg = False
    for block in section['blocks']:
      block = REWRITE.block(block)
      if prev_is_msg and TREE.is_newline(block):
        continue
      result['blocks'].append(block)
      prev_is_msg = REWRITE_RESULT.block_is_msg(block)

    result = REWRITE.discussion_section(result)
    return result

  @staticmethod
  def page(page):
    """ traverse: page -> section """
    return [REWRITE.section(section) for section in page]

  @staticmethod
  def note(note):
    page = PARSER.parse_file(FLAT.to_path(note))
    g.rewrite_note = note
    result = REWRITE.page(page)
    g.rewrite_note = dict()
    return result

@app.route('/api/parse/<note>')
def api_parse(note):
  page = PARSER.parse_file(FLAT.to_path(note))
  return {'note': note, 'page': page}

@app.route('/api/rewrite/<note>')
def get_rewrite(note):
  result = REWRITE.note(note)
  return {'result': result}
