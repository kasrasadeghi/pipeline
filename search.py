def block_generator():
  notes = FLAT.list_by_mtime()

  LOG({"file count": len(notes)})

  for note in notes:
    LOG({"searching through note": note})
    non_metadata_sections = list(filter(lambda x: x['title'] != 'METADATA', PARSER.parse_file(FLAT.to_path(note))))
    for S in reversed(non_metadata_sections):
      for B in S['blocks']:
        yield note, B

def msg_generator():
  for f, B in block_generator():
    match B:
      case [{ "value": content, "indent": 0, "children": [
              { "value": date, "indent": 1, "children": []}
           ]}]:
        if content.startswith('msg: ') and date.startswith('Date: '):
          yield {'content': content, 'block': B, 'origin': f}

def render_msg_from_generator(msg_gen_result):
  return DISCUSSION_RENDER.msg(REWRITE.block(msg_gen_result['block']) | {'origin': msg_gen_result['origin']})

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
  content = "".join(map(render_msg_from_generator, msgs))

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
      acc.append(render_msg_from_generator(msg))
  content = "".join(acc)

  DEBUG.set_state("content size", len(content))

  return SEARCH.RENDER(
    content,
    msg_count=msg_count,
    elapsed_time=(time.time() - DEBUG.get_state("start time"))
  )
