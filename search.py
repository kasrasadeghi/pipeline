@app.route('/search')
def get_search():
  files = list(reversed(FLAT.list_by_create_date()))

  acc = []

  for f in files:
    print("LOG: searching through file: " + f)
    for blocks in reversed(parse_file(FLAT.to_path(f))):
      for B in blocks:
        if isinstance(B, dict):
          if B['value'].startswith("msg:"):
            acc.append(B)
  print(len(acc))
  import time
  start = time.time()
  content = "".join(map(DISCUSSION.RENDER_MSG, acc))
  print(time.time() - start)
  print(len(files))
  print(len(content))
  return DEBUG.TEXT("search", content)

@app.route('/search/<query>')
def get_search_with_query(query):

  def condition(B):
    return query in B['value']

  files = list(reversed(FLAT.list_by_create_date()))

  acc = []

  for f in files:
    print(f)
    for blocks in reversed(parse_file(FLAT.to_path(f))):
      for B in blocks:
        if isinstance(B, dict):
          if B['value'].startswith("msg:"):
            if condition(B):
              acc.append(B)
  import time
  start = time.time()
  content = "".join(map(DISCUSSION.RENDER_MSG, acc))
  print(time.time() - start)
  print(len(files))
  return DEBUG.TEXT("search", content)
