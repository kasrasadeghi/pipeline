@app.route('/tool/journal_by_date')
def list_journals():
  r = []
  for note in FLAT.list():
    x = REWRITE.note(note)
    assert x[-1]['title'] == 'METADATA'
    m = FLAT.parse_metadata_from_section(x[-1])
    if 'Tags' in m and 'Journal' in m['Tags']:
      parts = m['Title'].split(' ')
      parts[1] = parts[1].removesuffix(',')
      d = {}
      d['m'], d['d'], d['y'] = parts
      d = DATECALC.date_to_nums(d)
      r.append({'t': m['Title'], 'd': d, 'n': note})
  r.sort(key=lambda x: DATECALC.date_tuple(x['d']))
  return '<pre>' + FLASK_UTIL.ESCAPE(json.dumps(r, indent=2)) + '</pre>'
