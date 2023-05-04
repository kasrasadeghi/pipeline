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
    sections = [{"title":"entry", "lines":[]}]
    for l in content.split('\n'):
      if l.startswith("--- ") and l.endswith(" ---") and len(l) > 9:
        sections.append({"title": l.removeprefix("--- ").removesuffix(" ---"), "lines":[]})
      else:
        sections[-1]["lines"].append(l)

    for S in sections:
      if S['title'] not in ('METADATA', 'HTML'):
        S['blocks'] = PARSER.parse_section(S['lines'], **kwargs)
        del S['lines']

    return sections

  @staticmethod
  def parse_section(lines, **kwargs):
    """turns a list of lines into a list of blocks"""

    tree_parser = kwargs.get('tree_parser', TREE_PARSER.process_block)

    blocks = []
    for l in lines:
      if l.strip() == '':
        blocks.append([])
      else:
        if len(blocks) == 0 or len(blocks[-1]) == 0:
          blocks.append([])
        blocks[-1].append(l)
    return [tree_parser(b, **kwargs) for b in blocks]
