class LineReader:
  def __init__(R, content):
    R.lines = content.splitlines()
    R.i = 0

  def peek(R):
    return R.lines[R.i]

  def get(R):
    R.i += 1
    return R.i - 1, R.lines[R.i - 1][:-1]

  def hasNext(R):
    return R.i < len(R.lines)

def parse_file(filepath):
  with open(filepath) as f:
    return parse_content(f.read())

def parse_content(content):
  R = LineReader(content)

  # EXPL: a file is a list of blocks, which are each a list of lines
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
  return FLAT_RENDER.TEXT('test_parse', "\n\n".join(map(str, parse_file(FLAT.to_path(note)))))
