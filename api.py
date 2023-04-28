@app.route('/test/parse/<note>')
def test_parse(note):
  page = PARSER.parse_file(FLAT.to_path(note))
  return DEBUG.TEXT('test_parse', TREE.dump_tree(page))

@app.route('/api/parse/<note>')
def api_parse(note):
  page = PARSER.parse_file(FLAT.to_path(note))
  return {'note': note, 'page': page}

@app.route('/api/rewrite/<note>')
def get_rewrite(note):
  result = REWRITE.note(note)
  return {'note': note, 'rewrite': result}
