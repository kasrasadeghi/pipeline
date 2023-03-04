# tree shaping utilities

class TREE:
  @staticmethod
  def filesize(note):
    return f"<pre><br/>(file size: {os.path.getsize(FLAT.to_path(note))} bytes)</pre>"

  @staticmethod
  def is_newline(block):
    """ a newline block looks like this: [''] """
    return len(block) == 1 and block[0] == ''

  @staticmethod
  def is_line(block):
    """ a line is a block with one item that is a string, not a parse tree item """
    return len(block) == 1 and isinstance(block[0], str)

  @staticmethod
  def dump_tree(page):
    acc = list()
    for S in page:
      acc.append(S['title'])
      for B in S['blocks']:
        if len(B) == 1:
          acc.append(FLASK_UTIL.ESCAPE(B))
        else:
          debug('huh', B, debugmode='ACTIVE')
          acc.append('[')
          for EL in B:
            acc.append(' ' + FLASK_UTIL.ESCAPE(EL))
          acc.append(']')
    return "\n".join(acc)
