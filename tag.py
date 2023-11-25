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

    i = 0
    while i < len(content):
      if content[i].isupper():
        uppercase_prefix = content[i]
        i += 1
        # parse uppercase prefix, including intermediate dashes and underscores
        while i < len(content) and (
            content[i].isupper() or (content[i] in '-_' and i+1 < len(content) and content[i+1].isupper())
        ):
          uppercase_prefix += content[i]
          i += 1

        # it doesn't count as a tag if it's not long enough (at least 2 chars long),
        # just parse plain text until we hit a tag
        if len(uppercase_prefix) < 2:
          non_uppercase_prefix = uppercase_prefix
          while i < len(content) and not content[i].isupper():
            non_uppercase_prefix += content[i]
            i += 1
          acc.append(non_uppercase_prefix)
        else:
          acc.append({'tag': uppercase_prefix})
      else:
        non_uppercase_prefix = content[i]
        i += 1
        while i < len(content) and not content[i].isupper():
          non_uppercase_prefix += content[i]
          i += 1
        acc.append(non_uppercase_prefix)

    return acc

# tests:
# SnaKeCaSE teST -> SE ST
# HUH- TEST -> HUH TEST, not the -
# TEST--but -> TEST, not the --
# I think a lot about PIPELINE -> PIPELINE, not the 'I'
