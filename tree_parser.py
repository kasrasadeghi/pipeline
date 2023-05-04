class TREE_PARSER:
  @staticmethod
  def process_block(block, **kwargs):
    def mknd(indent, line):
      return {"indent":indent, "value":line, "children":[]}

    indent_lines = []
    for l in block:
      if l.startswith('- '):
        indent_lines.append((0, l.removeprefix('- ')))
      elif l.startswith(' '):
        indent = len(l) - len(l.lstrip())
        if indent % 2 != 0:
          return block  # failure case
        if not l.lstrip().startswith('- '):
          return block
        indent_lines.append((indent // 2, l.lstrip().removeprefix('- ')))
      else:
        indent_lines.append((-1, l))

    roots = []
    stack = []
    found_children = False
    for indent, l in indent_lines:
      while stack and stack[-1]["indent"] >= indent:
        stack.pop()

      if not stack:
        if indent in (-1, 0):
          node = mknd(indent, l)
          stack.append(node)
          roots.append(node)
          continue
        else:
          return block  # failure case

      # else, stack has elements on it
      found_children = True

      node = mknd(indent, l)
      if stack[-1]["indent"] + 1 != indent:
        return block  # failure case
      stack[-1]["children"].append(node)
      stack.append(node)

    if not found_children:
      return block

    return roots
