class ADV_TREE_PARSER:
  INDENT_TOPLEVEL = -1

  @staticmethod
  def process_block(B, **kwargs):
    if ADV_TREE_PARSER.might_be_tree(B, **kwargs):
      return ADV_TREE_PARSER.parse_tree(B, **kwargs)
    else:
      return B


  @staticmethod
  def count_spaces(L):
    """ returns (idx, dash) where idx is the first non-space character and dash is whether that character is a dash"""
    for spaces, c in enumerate(L):
      if c != ' ':
        is_dash = c == '-'
        return DICT(spaces, is_dash)
    return DICT(spaces=0, is_dash=False)

  @staticmethod
  def might_be_tree(B, **kwargs):
    if TREE.is_newline(B):
      return False

    indents = [ADV_TREE_PARSER.count_spaces(L) for L in B]  # list of (space_count, is_dash)

    for i, indent in enumerate(indents):
      if indent.spaces % 2 != 0:
        LOG({'line#': i, 'line': B[i], 'uneven indent': indent})
        return False

    prev = None
    for indent, L in zip(indents, B):
      # initial is indent 0, dashed or not
      if prev is None:
        if indent.spaces == 0:
          prev = indent
        else:
          return False

      normalize_spaces = lambda x: x.spaces + 2 if x.is_dash else x.spaces
      prev_spaces = normalize_spaces(prev)
      curr_spaces = normalize_spaces(indent)
      if curr_spaces > prev_spaces + 4:
        LOG({'curr': curr_spaces, 'prev': prev_spaces})
        return False

    return True

  @staticmethod
  def parse_tree(block, **kwargs):
    LOG({"parse tree from block": block})
    indent_counts = []
    for L in block:
      LOG({"L": L})
      if L[0] != ' ' and L[0] != "-":
        indent_counts.append({"indent": 0, "content": L})
      else:
        spaces = ADV_TREE_PARSER.count_spaces(L).spaces
        assert(spaces % 2 == 0)
        indent_counts.append({"indent": spaces // 2, "content": L.lstrip()})

    def make_node(content, children, indent):
      return {"indent": indent, 'value': content, 'children': children}

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
        result.append(make_node(content, children, level))

      #   return acc
      return result

    return make_children(indent_counts)

@app.route('/advparse/<note>')
def test_advparse(note):
  page = PARSER.parse_file(FLAT.to_path(note), tree_parser=ADV_TREE_PARSER.process_block)
  return DEBUG.TEXT('test_parse', PRETTY.DUMP(page, no_symbol=False))
