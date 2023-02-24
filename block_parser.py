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

# ---------------------------------------------------------------------------- #

class PARSER:
  @staticmethod
  def parse_file(filepath, **kwargs):
    with open(filepath) as f:
      return PARSER.parse_content(f.read(), **kwargs)

  @staticmethod
  def parse_content(content, **kwargs):
    # EXPL: a file is a list of sections, which each have a title and a list of blocks
    # - a block is a list of nodes
    # - a node can be either a line of type 'str', or a parsed tree
    R = LineReader(content)

    make_section = lambda title: {"title": title, "lines": list()}

    sections = list()
    curr_section = make_section("entry")

    while R.hasNext():
      i, L = R.get()
      if L.startswith("--- ") and L.endswith(" ---"):
        # end previous section
        sections.append(curr_section)

        title = L[len("--- "):-len(" ---")]
        if not all(map(lambda c: c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ ', title)):
          LOG(f"WARNING: invalid section title '{title}'")
        curr_section = make_section(title)
      else:
        curr_section['lines'].append(L)
    sections.append(curr_section)

    for S in sections:
      S['blocks'] = PARSER.parse_section("\n".join(S['lines']), **kwargs)

    return sections

  @staticmethod
  def parse_section(section, **kwargs):
    R = LineReader(section)
    # EXPL: a section is a list of blocks, which are each a list of lines
    blocks = []
    curr_block = []
    while R.hasNext():
      i, l = R.get()

      if "" == l:
        if len(curr_block):
          blocks.append(curr_block)
        blocks.append([''])
        curr_block = []
      else:
        curr_block.append(l)

    # avoids empty blocks at the end of sections
    if len(curr_block):
      blocks.append(curr_block)

    new_blocks = []
    for B in blocks:
      if 'tree_parser' in kwargs:
        new_blocks.append(kwargs['tree_parser'](B, **kwargs))
      else:
        new_blocks.append(TREE_PARSER.process_block(B, **kwargs))
    return new_blocks

@app.route('/parse/<note>')
@app.route('/test/parse/<note>')
def test_parse(note):
  page = PARSER.parse_file(FLAT.to_path(note))
  return DEBUG.TEXT('test_parse', TREE.dump_tree(page))
