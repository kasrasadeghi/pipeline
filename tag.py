class TAG:
  def gather(content):
    def is_tag(x):
      match x:
        case {'tag': _}:
          return True
        case _:
          return False
    return list(filter(is_tag, TAG.parse(content)))

  def parse(content):
    acc = list()

    if content[:1] == '\\':
      if (cmdlen := content.find(' ')) == -1:
        cmdlen = len(content)
      acc.append({'cmd': content[:cmdlen]})
      content = content[cmdlen:]

    tag = None
    rest = None
    for c in content:
      if c.isupper():
        # print('u ' + c, word, rest)

        if tag:
          tag += c
        else:
          tag = c
      else:
        # print('  ' + c, word, rest)

        if tag:
          if len(tag) == 1:
            if rest:
              rest += tag
            else:
              rest = tag
            tag = None
          else:
            # we should delay pushing 'rest' until we're sure we're parsing a tag
            # we can delay it all the way until we're pushing the tag itself
            if rest:
              acc.append(rest)
              rest = None
            acc.append({'tag': tag})
            tag = None
        if rest:
          rest += c
        else:
          rest = c

    # print('end', word, rest)

    if rest:
      acc.append(rest)
      rest = None

    if tag:
      acc.append({'tag': tag})
      tag = None

    # print('end', word, rest)

    return acc
