class REWRITE:
  @staticmethod
  def block(block, **kwargs):
    if DISCUSSION.block_is_msg(block):
      return {'date': DISCUSSION.date(block[0]), 'msg': DISCUSSION.msg_content(block[0])}
    return block

  @staticmethod
  def section(section, **kwargs):
    acc = {'blocks': list()}
    for block in section['blocks']:
      acc['blocks'].append(REWRITE.block(block, **kwargs))
    return acc

  @staticmethod
  def page(page, **kwargs):
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
