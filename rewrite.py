class REWRITE:
  @staticmethod
  def page(page, **kwargs):
    return page

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
