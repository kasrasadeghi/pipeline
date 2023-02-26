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

    word = None
    rest = None
    for c in content:
      if c.isupper():
        print('u ' + c, word, rest)

        if rest:
          acc.append(rest)
          rest = None

        if word:
          word += c
        else:
          word = c
      else:
        print('  ' + c, word, rest)

        if word:
          if len(word) == 1:
            acc.append(word)
            word = None
          else:
            acc.append({'tag': word})
            word = None
        if rest:
          rest += c
        else:
          rest = c

    assert not (word and rest)

    print('end', word, rest)

    if word:
      acc.append({'tag': word})
      word = None
    if rest:
      acc.append(rest)
      rest = None

    print('end', word, rest)

    return acc
