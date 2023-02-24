class REWRITE_RESULT:
  @staticmethod
  def block_is_msg(block):
    return isinstance(block, dict) and 'date' in block and 'msg' in block

class REWRITE:
  context = dict()

  @staticmethod
  def line(line):
    # cont is continuation
    # base is the escape function for when we have no more rendering left to do
    def parse_url(S, cont, base):
      if ': ' in S:
        prefix, url = S.rsplit(': ', 1)
        url = url.strip()

        if url.startswith('https://'):
          return cont(prefix, base) + [": ", {'link': url}]

        if url.endswith(".note") and \
           FLAT.note_id_len() == len(url.strip()):
          return cont(prefix, base) + [": ", {'note': url}]

        if url.startswith('/'):
          return cont(prefix, base) + [": ", {'internal-link': url}]

        if url.startswith(FLASK_UTIL.URL_ROOT()):
          from urllib.parse import unquote_plus
          return cont(prefix, base) + [": ", {'url-internal-link': unquote_plus(url)}]

      return cont(S, base)

    def highlight_tags(S, base):
      return base(S)

    return parse_url(line, cont=highlight_tags, base=lambda x: [x])

  @staticmethod
  def block(block):
    """ rewrite: block -> (| message block)"""
    match block:
      case [{ "value": content, "indent": 0, "children": [
              { "value": date, "indent": 1, "children": []}
           ]}]:
        return {'msg': REWRITE.line(content), 'date': date}
    return block

  @staticmethod
  def section(section):
    """ transform: section -> block """
    result = {'title': section['section'], 'blocks': list()}
    prev_is_msg = False
    for block in section['blocks']:
      block = REWRITE.block(block)
      if prev_is_msg and TREE.is_newline(block):
        continue
      result['blocks'].append(block)
      prev_is_msg = REWRITE_RESULT.block_is_msg(block)

    return result

  @staticmethod
  def page(page):
    """ traverse: page -> section """
    return [REWRITE.section(section) for section in page]

  @staticmethod
  def note(note):
    page = PARSER.parse_file(FLAT.to_path(note))
    REWRITE.context['note'] = note
    result = REWRITE.page(page)
    REWRITE.context = dict()
    return result

@app.route('/api/parse/<note>')
def api_parse(note):
  page = PARSER.parse_file(FLAT.to_path(note))
  return {'note': note, 'page': page}

@app.route('/api/rewrite/<note>')
def get_rewrite(note):
  result = REWRITE.note(note)
  return {'result': result}
