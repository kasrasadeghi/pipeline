def block_generator():
  notes = list(reversed(list(map(lambda p: p[0],
                                 util.sort_mtime(map(lambda n: (n, FLAT.to_path(n)), FLAT.list()),
                                                 key=lambda p: p[1])))))

  LOG({"file count": len(notes)})

  for note in notes:
    LOG({"searching through note": note})
    non_metadata_sections = list(filter(lambda x: x['title'] != 'METADATA', REWRITE.note(note)))
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
    return RENDER.base_page({'title': 'search', 'content': content})

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
  msg_count = 0
  for msg in msg_generator():
    if query.lower() in msg['content'].lower():
      if current_note != msg['origin']:
        acc.append(RENDER_UTIL.banner(FLAT.title(msg['origin'])))
        current_note = msg['origin']
      msg_count += 1
      acc.append(DISCUSSION_RENDER.msg(REWRITE.block(msg)))
  content = "".join(acc)

  DEBUG.set_state("content size", len(content))

  return SEARCH.RENDER(
    content,
    msg_count=msg_count,
    elapsed_time=(time.time() - DEBUG.get_state("start time"))
  )
