class TAG:
  @staticmethod
  def gather(content):
    def is_tag(x):
      match x:
        case {'tag': _}:
          return True
        case _:
          return False
    return list(filter(is_tag, TAG.parse(content)))

  @staticmethod
  def parse(content):
    acc = list()

    if content[:1] == '\\':
      if (cmdlen := content.find(' ')) == -1:
        cmdlen = len(content)
      acc.append({'cmd': content[:cmdlen]})
      content = content[cmdlen:]

    tag = None
    plain = None
    def acc_plain(c):
      nonlocal plain
      if plain:
        plain += c
      else:
        plain = c

    def flush_plain():
      nonlocal plain
      nonlocal acc
      if plain:
        acc.append(plain)
        plain = None

    def acc_tag(c):
      nonlocal tag
      if tag:
        tag += c
      else:
        tag = c

    def flush_tag():
      nonlocal tag
      nonlocal acc
      if tag:
        acc.append({'tag': tag})
        tag = None

    def acc_current(c):
      nonlocal tag
      nonlocal plain
      if not tag and not plain:
        acc_plain(c)
      elif tag:
        tag += c
      elif plain:
        plain += c

    # actual parsing loop doing the work
    for c in content:
      if c in '-_':
        acc_current(c)
        continue
      if not c.isupper():
        flush_tag()
        acc_plain(c)
      else:
        flush_plain()
        acc_tag(c)

    flush_plain()
    flush_tag()

    # ignore tags that are one character long
    result = []
    for el in acc:
      match el:
        case {'tag': t} as x:
          if len(t) == 1:
            result.append(t)
          else:
            result.append(x)
        case _ as p:
          result.append(p)

    return result
