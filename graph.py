
@app.route("/graph")
def get_graph():
  def title(note):
    if note in FLAT.list():
      return FLAT.title(note)
    else:
      return note

  def link(note):
    if note in FLAT.list():
      return f'<a href="{FLAT.to_url(note)}">{FLAT.title(note)}</a>'
    else:
      return note

  def legible_setdict(d):
    legible_result = list()
    for key, value in d.items():
      legible_result.append(link(key) + ":\n")
      ps = [(link(x), title(x)) for x in value]
      ps.sort(key=lambda p: p[1])
      for p in ps:
        legible_result.append("  " + p[0] + "\n")
    return "".join(legible_result)

  backlinks, refmap = FLAT.backlinks_refmap()

  limit = len(refmap)
  if 'limit' in request.args:
    limit = int(request.args.get('limit'))
  actual = list(refmap)[0:limit]

  unionfind = {x: x for x in actual}

  def find(note):
    if note == unionfind[note]:
      return note
    return find(unionfind[note])

  def union(note, other):
    other_rep = find(other)
    children = set()
    for child, parent in unionfind.items():
      if parent == other_rep:
        children.add(child)
    note_rep = find(note)
    for child in children:
      unionfind[child] = note_rep

  for note in actual:
    for other in refmap[note]:
      if other in actual and find(note) != find(other):
        union(note, other)

    if note in backlinks:
      for other in backlinks[note]:
        if other in actual and find(note) != find(other):
          union(note, other)

  result = dict()
  for key, value in unionfind.items():
    if value not in result:
      result[value] = set()
    result[value].add(key)

  return DEBUG.TEXT("refs", legible_setdict(result))
