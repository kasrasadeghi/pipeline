class LineReader:
  def __init__(R, content):
    R.lines = content.split('\n')
    R.i = 0

  def peek(R):
    return R.lines[R.i]

  def get(R):
    R.i += 1
    return R.i - 1, R.lines[R.i - 1]

  def hasNext(R):
    return R.i < len(R.lines)

def parse_file(filepath):
  with open(filepath) as f:
    return parse_content(f.read())

def parse_content(content):
  # EXPL: a file is a list of sections, which each have a title and a list of blocks
  # - a block is a list of nodes
  # - a node can be either a line of type 'str', or a parsed tree
  R = LineReader(content)

  make_section = lambda title: {"section": title, "content": list()}

  sections = list()
  curr_section = make_section("entry")

  while R.hasNext():
    i, L = R.get()
    if L.startswith("--- ") and L.endswith(" ---"):
      sections.append(curr_section)

      title = L[len("--- "):-len(" ---")]
      if not all(map(lambda c: c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ ', title)):
        print(f"WARNING: invalid section title '{title}'")
      curr_section = make_section(title)
    else:
      curr_section['content'].append(L)
  sections.append(curr_section)

  for S in sections:
    S['blocks'] = parse_section("\n".join(S['content']))
    del S['content']

  return sections

def parse_section(section):
  R = LineReader(section)
  # EXPL: a section is a list of blocks, which are each a list of lines
  blocks = []
  curr_block = []
  while R.hasNext():
    i, l = R.get()

    if "" == l:
      if 0 != len(curr_block):
        blocks.append(curr_block)
        curr_block = []
      continue
    else:
      curr_block.append(l)

  if 0 != len(curr_block):
    blocks.append(curr_block)
    curr_block = []

  new_blocks = []
  for B in blocks:
    if might_be_tree(B):
      new_blocks.append(parse_tree(B))
    else:
      new_blocks.append(B)

  return new_blocks

def might_be_tree(B):
  indent_counts = []
  for i, L in enumerate(B):
    # search for toplevels
    if L[0] != ' ' and L[0] != "-" and len(B) > i + 1 and B[i + 1].startswith("-"):
      indent_counts.append(-1)
      continue
    else:
      if not L.lstrip():
        return False
      if "-" != L.lstrip()[0]:
        return False

    indent, rest = L.split("-", 1)
    indent_counts.append(len(indent) // 2)

  prev = None
  for indent, L in zip(indent_counts, B):
    # initial is toplevel or zero/0 indent
    if prev is None \
       and (indent == 0 or indent == -1):
      prev = indent
      continue

    # child element
    if prev is not None and indent == prev + 1:
      prev = indent
      continue

    # reset to sibling or ancestor
    if prev is not None and indent <= prev:
      prev = indent
      continue

    # if no successful condition found, this line has failed
    print("ERROR: failed on", prev, "->", indent, L)
    return False

  return True

def parse_tree(block):
  indent_counts = []
  for L in block:
    if L[0] != ' ' and L[0] != "-":
      indent_counts.append({"indent": -1, "content": L})
      continue
    indent, rest = L.split("-", 1)
    assert all(' ' == c for c in indent),  "error with line: " + L
    indent_counts.append({"indent": len(indent) // 2, "content": rest.lstrip()})

  def make_node(content, children):
    return {'value': content, 'children': children}

  # from: https://github.com/kasrasadeghi/cornerstone-haskell/blob/master/src/Parse.hs#L50-L59
  def make_children(B):
    result = []
    rest = B

    while 0 != len(rest):
      level, content = rest[0]['indent'], rest[0]['content']
      rest = rest[1:]
      # collect children of this node,
      #   which are the prefix of _rest_ that have a level that is greater than this node
      acc = []
      while True:
        if 0 == len(rest):
          break
        if rest[0]['indent'] <= level:
          break
        acc.append(rest[0])
        rest = rest[1:]

      children = make_children(acc)
      result.append(make_node(content, children))

    #   return acc
    return result

  return make_children(indent_counts)

@app.route('/parse/<note>')
def test_parse(note):
  acc = list()
  for S in parse_file(FLAT.to_path(note)):
    acc.append(S['section'])
    for B in S['blocks']:
      acc.append(str(B))

  return DEBUG.TEXT('test_parse', "\n".join(acc))
