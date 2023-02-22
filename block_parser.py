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
    if 'tree_parser' not in kwargs:
      kwargs['tree_parser'] = TREE_PARSER.process_block
    with open(filepath) as f:
      return PARSER.parse_content(f.read(), **kwargs)

  @staticmethod
  def parse_content(content, **kwargs):
    # EXPL: a file is a list of sections, which each have a title and a list of blocks
    # - a block is a list of nodes
    # - a node can be either a line of type 'str', or a parsed tree
    R = LineReader(content)

    make_section = lambda title: Texp("section", Texp('title', title), Texp("lines"))

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
        curr_section['lines'].push(Texp('line', L))
    sections.append(curr_section)

    for S in sections:
      blocks, tree_blocks = PARSER.parse_section(S, **kwargs)
      S.push(blocks)
      S.push(tree_blocks)

    return Texp('page', *sections)

  @staticmethod
  def parse_section(section, **kwargs):
    blocks = Texp('blocks')
    curr_block = Texp('block')
    for line in section['lines']:
      if "" == line.get():
        if len(curr_block):
          blocks.push(curr_block)
        blocks.push(Texp('newline'))
        curr_block = Texp('block')
      else:
        curr_block.push(line)

    # avoids empty blocks at the end of sections
    if len(curr_block):
      blocks.push(curr_block)

    tree_blocks = Texp('trees')
    for B in blocks:
      tree_blocks.push(kwargs['tree_parser'](B, **kwargs))
    return blocks, tree_blocks

@app.route('/parse/<note>')
@app.route('/test/parse/<note>')
def test_parse(note):
  page = PARSER.parse_file(FLAT.to_path(note))
  return DEBUG.TEXT('test_parse', TREE.dump_tree(page))

def dump_parse(page):
  new_page = Texp('page')
  for sec in page:
    LOG({'sec', sec})
    new_page.push(Texp('section', sec['title'], sec['trees']))
  dump = new_page.format('page', 'section', 'blocks', 'block', 'lines', 'acc', 'newline', 'trees')
  return '<pre>' + str(len(dump)) + dump + "</pre>"

@app.route('/api/parse/<note>')
def api_parse(note):
  page = PARSER.parse_file(FLAT.to_path(note))
  return dump_parse(page)

@app.route('/api/block_parse/<note>')
def api_block_parse(note):
  page = PARSER.parse_file(FLAT.to_path(note), tree_parser=lambda x, **kw: x)
  return dump_parse(page)
