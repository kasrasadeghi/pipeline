def block_generator():
  files = list(reversed(FLAT.list_by_create_date()))
  set_state("file count", len(files))

  for f in files:
    LOG("searching through file: " + f)
    non_metadata_sections = list(filter(lambda x: x['section'] != 'METADATA',
                                        parse_file(FLAT.to_path(f))))
    for S in reversed(non_metadata_sections):
      for B in S['blocks']:
        yield B

def msg_generator():
  for B in block_generator():
    for L in B:
      if isinstance(L, dict) and L['value'].startswith("msg:"):
        yield L

@app.route('/search')
def get_search():
  init_state()

  import time
  start = time.time()

  acc = list()
  for msg in msg_generator():
    acc.append(msg)
  content = "".join(map(DISCUSSION.RENDER_MSG, msg_generator()))

  set_state("elapsed time", time.time() - start)
  set_state("msg count", len(acc))
  set_state("content size", len(content))
  return DEBUG.TEXT("search", content)


@app.route('/search/<query>')
def get_search_with_query(query):
  init_state()

  files = list(reversed(FLAT.list_by_create_date()))

  import time
  start = time.time()

  acc = list()
  for msg in msg_generator():
    if query in msg['value']:
      acc.append(msg)
  content = "".join(map(DISCUSSION.RENDER_MSG, acc))

  set_state("elapsed time", time.time() - start)
  set_state("msg count", len(acc))
  set_state("content size", len(content))
  return DEBUG.TEXT("search", content)
