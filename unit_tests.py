@app.route('/test/unit/render_msg')
def test_render_msg():
  msg = {
    'indent': 0,
    'value': 'msg: AWAKEN a bit ago, RECAP PLAY GAME vampire survivors',
    'children': [
      {
        'indent': 1,
        'value': 'Date: Tue Feb 14 11:13:50 PST 2023',
        'children': []
      }
    ]
  }
  kwargs = {
    'origin_note': 'd8362739-4333-4fef-8ddd-fddb1a7ca8e9.note'
  }
  for i in range(1000):
    DISCUSSION_RENDER.msg(msg, **kwargs)
  return 'DONE'

@app.route('/test/unit/date_cmd')
def test_date_cmd():
  for i in range(10000):
    util.date_cmd("-d", 'Tue Feb 14 11:13:50 PST 2023', "+%T")
  return 'DONE'

@app.route('/test/unit/render_every_note')
def test_render_every_note():
  for note in FLAT.list():
    DISCUSSION_RENDER.MAIN(note)
  return 'DONE'

@app.route('/test/unit/pagesize_every_note')
def test_pagesize_every_note():
  size = 0
  for note in FLAT.list():
    size += len(DISCUSSION_RENDER.MAIN(note))
  return 'rendered size: ' + str(size)

def eqch(*P):
  g = Texp('pass')
  b = Texp('fail')
  for i, p in enumerate(P):
    assert len(p) in {2, 3}
    if len(p) == 2:
      A, B = p
      v = f"#{i}: '{repr(A)}' == '{repr(B)}'"
    elif len(p) == 3:
      A, B, msg = p
      v = f"#{i}: '{repr(A)}' == '{repr(B)}', {msg}"
    try:
      if A == B:
        g.push(v)
      else:
        b.push(v)
    except Exception as e:
      raise Exception(v) from e
  return \
    "<p>FAIL</p>" + "<pre>" + "<br>".join(b) + "</pre>"\
    "<p>PASS</p>" + "<pre>" + "<br>".join(g) + "</pre>"

@app.route('/test/unit/texp_eq')
def test_texp_eq():
  return eqch(
    [Texp('indent'),
     Texp('indent')],

    [Texp('indent', Texp('a')),
     Texp('indent', Texp('a'))],

    [Texp('indent', 0),
     Texp('indent', 0)],

    [Texp('a', '"0"'),        # expect fail
     Texp('a', Texp('"0"'))]
  )

@app.route('/test/unit/texp_parse')
def test_texp_parse():
  return eqch(
    [Texp('indent', 0),
     Texp.parse('(indent 0)'),
     'nonquoted numbers are ints'],

    [Texp('indent', Texp('"0"')),
     Texp.parse('(indent "0")'),
     'quotes are strings'],

    [Texp('indent', Texp("'0'")),
     Texp.parse("(indent '0')"),
     'single quotes are also strings']
  )

@app.route('/test/unit/texp_pattern_match')
def test_texp_pattern_match():
  print(Texp('indent', 0).match('(indent {a})'))
  return eqch(
    [Texp('indent', 0).match('(indent {a})'),
     (True, '(match (a 0))')],

    [Texp('indent', '"0"').match('(indent {a})'),
     (True, '(match (a "0"))')],

    [Texp('indent', '"0"').match('(indent {a})'),
     (True, Texp.parse('(match (a "0"))'))]
  )
