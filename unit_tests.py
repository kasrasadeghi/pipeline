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
     [{'tag': 'HELLO'}, ' ', {'tag': 'WORLD'}]],
    [TAG.parse('INPUT generators vs stackless coroutines: QUOTE testing I am testing 1 2 3'),
     [{"tag": "INPUT"},
      " generators vs stackless coroutines: ",
      {"tag": "QUOTE"},
      " testing I am testing 1 2 3"],
     "capital 'I' should not disrupt parsing non-tags"]
  )

def total_size(o):
  # from: https://code.activestate.com/recipes/577504/
  from itertools import chain
  dict_handler = lambda d: chain.from_iterable(d.items())
  handlers = {tuple: iter,
              list: iter,
              dict: dict_handler,
              set: iter,
              frozenset: iter
              }
  seen = set()              # track which object id's have already been seen

  def sizeof(o):
    if id(o) in seen:       # do not double count the same object
      return 0
    seen.add(id(o))
    s = sys.getsizeof(o)
    if type(o) in handlers:
      try:
        s += sum(map(sizeof, handlers[type(o)](o)))  # get size of the objects it refers to as well
      except:
        import pdb
        pdb.set_trace()
    return s

  return sizeof(o)

@app.route('/test/unit/parse_all_memory')
def test_parse_all_memory():
  acc = list()
  for note in FLAT.list():
    acc.append(REWRITE.note(note))
  return str(total_size(acc))
