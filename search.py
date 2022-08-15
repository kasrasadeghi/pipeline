def block_generator():
  files = list(reversed(FLAT.list_by_create_date()))
  DEBUG.set_state("file count", len(files))

  for f in files:
    LOG("searching through file: " + f)
    non_metadata_sections = list(filter(lambda x: x['section'] != 'METADATA',
                                        PARSER.parse_file(FLAT.to_path(f))))
    for S in reversed(non_metadata_sections):
      for B in S['blocks']:
        yield f, B

def msg_generator():
  for f, B in block_generator():
    for L in B:
      if isinstance(L, dict) and L['value'].startswith("msg:"):
        assert 'origin' not in L
        L |= {'origin': f, 'date': DISCUSSION.date(L)}
        yield L

class SEARCH:
  @classmethod
  def RENDER(cls, content, **kwargs):
    content = (f'found {kwargs["msg_count"]} results '
               f'in {kwargs["elapsed_time"]} seconds '
               + content)
    return RENDER.base_page(DICT(content, title="search", bar=None))

  @staticmethod
  def msg(msg):
    origin = msg['origin']
    date = msg['date']

    return (f'<a href="/disc/{origin}#{date}">'
            + DISCUSSION_RENDER.msg(msg) +
            '</a>')

@app.route('/search')
def get_search():
  if 'content' in request.args:
    return redirect("/search/" + request.args['content'], code=302)

  DEBUG.init_state()

  msgs = list(msg_generator())
  content = "".join(map(DISCUSSION_RENDER.msg, msgs))

  DEBUG.set_state("content size", len(content))

  return SEARCH.RENDER(
    content,
    msg_count=(len(msgs)),
    elapsed_time=(time.time() - DEBUG.get_state("start time"))
  )

@app.route('/search/<query>')
def get_search_with_query(query):
  DEBUG.init_state()

  acc = list()
  current_note = None
  for msg in msg_generator():
    if query.lower() in msg['value'].lower():
      if current_note != msg['origin']:
        acc.append(RENDER.banner(FLAT.title(msg['origin'])))
        current_note = msg['origin']
      acc.append(SEARCH.msg(msg))
  content = "".join(acc)

  DEBUG.set_state("content size", len(content))

  return SEARCH.RENDER(
    content,
    msg_count=(len(msgs)),
    elapsed_time=(time.time() - DEBUG.get_state("start time"))
  )
