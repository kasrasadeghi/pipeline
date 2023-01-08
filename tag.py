class TAG:

  # TODO improve tag parsing to be "any sequence of capitalized letters".  maybe 2 or more, maybe 3 or more?
  def parse(msg_content):
    words = msg_content.split()
    acc = list()
    for word in words:
      if all(c.isupper() for c in word):
        acc.append(word)
    return acc
