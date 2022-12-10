class TAG:
  def parse(msg_content):
    words = msg_content.split()
    acc = list()
    for word in words:
      if all(c.isupper() for c in word):
        acc.append(word)
    return acc
