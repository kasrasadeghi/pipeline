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

@app.route('/api/get/<note>')
def get_raw_note(note):
  response = Response(FLAT.read_note(note), mimetype='text/plain')

  from urllib.parse import urlparse
  origin = urlparse(FLASK_UTIL.HEADERS()['Origin'])
  if 'localhost' in origin.netloc:
    response.headers['Access-Control-Allow-Origin'] = FLASK_UTIL.HEADERS()['Origin']
  return response
