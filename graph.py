class GRAPH:
  @staticmethod
  def backlinks_refmap():
    refmap = dict()
    for note in FLAT.list():
      refmap[note] = list(set(GRAPH.collect_refs(note)))

    backlinks = dict()  # maps from note to set of referrers
    for note, refs in refmap.items():
      for ref in refs:
        if ref not in backlinks:
          backlinks[ref] = set()
        backlinks[ref].add(note)

    return backlinks, refmap

  @staticmethod
  def collect_refs(note):
    """@returns a list of notes this note references in the order they appear"""
    with open(FLAT.to_path(note)) as f:
      lines = f.readlines()

    acc = list()
    def render_note(note, **kwargs):
      nonlocal acc
      acc.append(note)

    RENDER.content(note, render_note=render_note)

    return acc

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

  backlinks, refmap = GRAPH.backlinks_refmap()

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
