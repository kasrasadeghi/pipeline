class TREE_PARSER:
  @staticmethod
  def process_block(B, **kwargs):
    if TREE_PARSER.might_be_tree(B, **kwargs):
      return TREE_PARSER.parse_tree(B, **kwargs)
    else:
      return B


  @staticmethod
  def might_be_tree(B, **kwargs):
    indent_counts = []
    for i, L in enumerate(B):
      # search for toplevels, will have indent -1
      # - toplevels start with something other than ' ' and '-' and are _immediately followed_ by a subnode.
      # - n.b. this even handles toplevels halfway through a block
      if len(L) != 0 and L[0] not in {' ', '-'}\
         and len(B) > i + 1 and B[i + 1].startswith("-"):
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
      LOG(f"ERROR: failed guessing tree-ness on {prev} -> {indent}{L}")
      return False

    return True

  @staticmethod
  def parse_tree(block, **kwargs):
    indent_counts = []
    for L in block:
      if L[0] != ' ' and L[0] != "-":
        indent_counts.append(Texp('indent-count', Texp("indent", -1), Texp("content", L)))
      else:
        indent, rest = L.split("-", 1)
        assert all(' ' == c for c in indent),  "error with line: " + L
        indent_counts.append(Texp('indent-count', Texp("indent", len(indent) // 2), Texp("content", rest.lstrip())))

    def make_node(content, children, indent):
      return Texp('node', Texp("indent", indent), Texp('value', content), Texp('children', *children))

    # from: https://github.com/kasrasadeghi/cornerstone-haskell/blob/master/src/Parse.hs#L50-L59
    def make_children(B):
      result = []
      rest = B

      while 0 != len(rest):
        level, content = rest[0]['indent'][0], rest[0]['content'][0]
        rest = rest[1:]
        # collect children of this node,
        #   which are the prefix of _rest_ that have a level that is greater than this node
        acc = Texp('children')
        while True:
          if 0 == len(rest):
            break
          if rest[0]['indent'][0] <= level:
            break
          acc.push(rest[0])
          rest = rest[1:]

        children = make_children(acc)
        result.append(make_node(content, children, level))

      return result

    return make_children(indent_counts)
