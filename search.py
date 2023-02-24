def msg_generator():
  files = list(reversed(list(map(lambda p: p[0],
                                 util.sort_mtime(map(lambda n: (n, FLAT.to_path(n)), FLAT.list()),
                                                 key=lambda p: p[1])))))
  # files = list(reversed(FLAT.list_by_create_date()))  # CONSIDER list by modify date
  LOG({"file count": len(files)})

  for f in files:
    LOG({'search file': f})
    for S in filter(lambda x: x.get('title') != 'METADATA', TEXP_REWRITE.note(f)):
      assert S.value == 'section'
      if 'trees' in S:
        for tree in S['trees']:
          if tree.value == 'msg':
            yield f, tree

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
  for f, msg in msg_generator():
    if query.lower() in msg.get('content').lower():
      if current_note != f:
        acc.append(RENDER_UTIL.banner(FLAT.title(f)))
        current_note = f
      msg_count += 1
      acc.append(DISCUSSION_RENDER.msg(msg, origin=f))
  content = "".join(acc)

  DEBUG.set_state("content size", len(content))

  return SEARCH.RENDER(
    content,
    msg_count=msg_count,
    elapsed_time=(time.time() - DEBUG.get_state("start time"))
  )
