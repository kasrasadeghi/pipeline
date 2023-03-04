@app.route('/test/unit/render_msg')
def test_render_msg():
  msg = {'msg': 'AWAKEN a bit ago, RECAP PLAY GAME vampire survivors',
         'Date': 'Tue Feb 14 11:13:50 PST 2023'}
  for i in range(1000):
    DISCUSSION_RENDER.msg(msg)
  return 'DONE'

@app.route('/test/unit/date_cmd')
def test_date_cmd():
  for i in range(10000):
    DATE.cmd("-d", 'Tue Feb 14 11:13:50 PST 2023', "+%T")
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
  g = [] # pass
  b = [] # failed
  for i, p in enumerate(P):
    assert len(p) in {2, 3}, f"{p}, {len(p)}"
    if len(p) == 2:
      A, B = p
      v = f"#{i}: '{repr(A)}' == '{repr(B)}'"
    elif len(p) == 3:
      A, B, msg = p
      v = f"#{i}: '{repr(A)}' == '{repr(B)}', {msg}"
    try:
      if A == B:
        g.append(v)
      else:
        b.append(v)
    except Exception as e:
      raise Exception(v) from e
  return \
    "<p>FAIL</p>" + "<pre>" + "<br>".join(b) + "</pre>" + \
    "<p>PASS</p>" + "<pre>" + "<br>".join(g) + "</pre>"

@app.route('/test/unit/tag_parse')
def test_tag_parse():
  return eqch(
    [TAG.parse('HELLO WORLD'),
     [{'tag': 'HELLO'}, ' ', {'tag': 'WORLD'}]]
  )
