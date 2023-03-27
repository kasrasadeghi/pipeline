class PARSER:
  @staticmethod
  def parse_file(filepath, **kwargs):
    with open(filepath) as f:
      return PARSER.parse_content(f.read(), **kwargs)

  @staticmethod
  def parse_content(content, **kwargs):
    # EXPL: a page is a list of sections, which each have a title and a list of blocks
    # - a block is a list of nodes
    # - a node can be either a line of type 'str', or a parsed tree
    make_section = lambda title: {"title": title, "lines": list()}

    sections = list()
    curr_section = make_section("entry")

    for line in content.split('\n'):
      if line.startswith("--- ") and line.endswith(" ---"):
        sections.append(curr_section)  # end previous section

        title = line[len("--- "):-len(" ---")]
        is_capital = lambda c: 0 <= ord(c) - ord('A') < 26
        if not all(map(lambda c: c == ' ' or is_capital(c), title)):
          LOG(f"WARNING: invalid section title '{title}'")
        curr_section = make_section(title)
      else:
        curr_section['lines'].append(line)
    sections.append(curr_section)

    for S in sections:
      if S['title'] == 'METADATA':
        continue
      S['blocks'] = PARSER.parse_section(S['lines'], **kwargs)
      del S['lines']

    return sections

  @staticmethod
  def parse_section(lines, **kwargs):
    """turns a list of lines into a list of blocks"""

    tree_parser = kwargs.get('tree_parser', TREE_PARSER.process_block)

    blocks = []
    curr_block = []
    for line in lines:
      if "" == line:
        if len(curr_block):
          blocks.append(tree_parser(curr_block, **kwargs))
        blocks.append([''])
        curr_block = []
      else:
        curr_block.append(line)

    # avoids empty blocks at the end of sections
    if len(curr_block):
      blocks.append(tree_parser(curr_block, **kwargs))

    return blocks

@app.route('/test/parse/<note>')
def test_parse(note):
  page = PARSER.parse_file(FLAT.to_path(note))
  return DEBUG.TEXT('test_parse', TREE.dump_tree(page))
