@app.route('/test/parse/<note>')
def test_parse(note):
  page = PARSER.parse_file(FLAT.to_path(note))
  return DEBUG.TEXT('test_parse', TREE.dump_tree(page))
