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
        L |= {'origin': f}
        yield L

class SEARCH:
  @classmethod
  def RENDER(cls, content):
    return DEBUG.TEXT("search",
                      f'found {DEBUG.get_state("msg count")} results '
                      f'in {DEBUG.get_state("elapsed time")} seconds '
                      + content)


@app.route('/search')
def get_search():
  if 'content' in request.args:
    return redirect("/search/" + request.args['content'], code=302)

  DEBUG.init_state()

  msgs = list(msg_generator())
  content = "".join(map(DISCUSSION_RENDER.msg, msgs))

  DEBUG.set_state("elapsed time", time.time() - DEBUG.get_state("start time"))
  DEBUG.set_state("msg count", len(msgs))
  DEBUG.set_state("content size", len(content))

  return SEARCH.RENDER(content)


@app.route('/search/<query>')
def get_search_with_query(query):
  DEBUG.init_state()

  acc = list()
  for msg in msg_generator():
    if query.lower() in msg['value'].lower():
      acc.append(msg)
  content = "".join(map(DISCUSSION_RENDER.msg, acc))

  DEBUG.set_state("elapsed time", time.time() - DEBUG.get_state("start time"))
  DEBUG.set_state("msg count", len(acc))
  DEBUG.set_state("content size", len(content))

  return SEARCH.RENDER(content)
