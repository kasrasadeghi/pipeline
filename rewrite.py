class REWRITE_RESULT:
  @staticmethod
  def block_is_msg(block):
    return isinstance(block, dict) and 'date' in block and 'msg' in block

class REWRITE:
  @staticmethod
  def line(line, **kwargs):
    # cont is continuation
    # base is the escape function for when we have no more rendering left to do
    def parse_url(S, cont, base):
      nonlocal kwargs

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
  def block(block, **kwargs):
    """ rewrite: block -> (| message block)"""
    if DISCUSSION.block_is_msg(block):
      return {'date': DISCUSSION.date(block[0]), 'msg': REWRITE.line(DISCUSSION.msg_content(block[0]), **kwargs)}
    return block

  @staticmethod
  def section(section, **kwargs):
    """ transform: section -> block """
    acc = {'blocks': list()}
    prev_is_msg = False
    for block in section['blocks']:
      block = REWRITE.block(block, **kwargs)
      if prev_is_msg and TREE.is_newline(block):
        continue
      acc['blocks'].append(block)
      prev_is_msg = REWRITE_RESULT.block_is_msg(block)
    return acc

  @staticmethod
  def page(page, **kwargs):
    """ traverse: page -> section """
    acc = list()
    for section in page:
      acc.append(REWRITE.section(section, **kwargs))
    return acc

@app.route('/api/parse/<note>')
def api_parse(note):
  page = PARSER.parse_file(FLAT.to_path(note))
  result = {'note': note, 'page': page}
  return json.dumps(result)

@app.route('/api/rewrite/<note>')
def get_rewrite(note):
  page = PARSER.parse_file(FLAT.to_path(note))
  result = REWRITE.page(page)
  return {'result': result}
  # return json.dumps(result, indent=2)
