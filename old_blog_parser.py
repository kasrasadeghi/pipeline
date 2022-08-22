class BLOG_PARSER:
  @staticmethod
  def linkify(x):
    if "https://" in x:
      index = x.index("https://")
      return x[:index] + f'<a href="{x[index:]}">' + x[index:]+ '</a>'
    return x

  @staticmethod
  def content(filepath):
    acc = []

    with open(filepath) as f:
      R = LineReader(f.read())

    state = dict()
    state['mode'] = None
    state['list_item_number'] = None

    deferred = list()
    def defer(item):
      deferred.append(item)

    while R.hasNext():
      for item in reversed(deferred):
        acc.append(item)
      deferred = list()

      i, l = R.get()

      if "--- METADATA ---" == l:
        break

      if "--- DISCUSSION ---" == l:
        break

      # parse list
      if 'list' == state['mode']:
        if l.startswith("- "):
          l = l[2:]

          if state['list_item_number'] == 0:
            acc.append('<li>')
          else:
            acc.append('</li><li>')
          state['list_item_number'] += 1

          # parse links
          if l.startswith("link:"):
            link = l.split("link:", 1)[1]
            acc.append(f'<a href="{link}">{link}</a>')
            continue

          # no continue to process contents of list item

        elif l.startswith("  "):
          pass
        else:
          state['mode'] = None
          acc.append('</li></ul>')

      if None == state['mode'] and R.hasNext() and R.peek().startswith("-"):
        state['mode'] = 'list'
        state['list_item_number'] = 0
        defer('<ul class="list">')

      # parse section title
      if 'section title' == state['mode']:
        if l.startswith(" |"):
          acc.append(l[len(" |"):])
          continue

        if l.startswith(" +"):
          acc.append("</h2>")
          state['mode'] = None
          continue

      if None == state['mode'] and l.startswith(" |"):
        state['mode'] = 'section title'
        acc.append('<h2>')
        acc.append(l[len(" |"):])
        continue

      # parse subsection title
      if 'subsection title' == state['mode']:
        # ignore bar
        acc.append("</h3>")
        state['mode'] = None
        continue

      if None == state['mode'] \
         and l.startswith(" " * 4) \
         and R.hasNext() \
         and R.peek().startswith((" " * 4) + "-") \
         and all(x == "-" for x in R.peek().strip()):
        state['mode'] = 'subsection title'
        acc.append('<h3>')
        acc.append(l)
        continue

      if l.startswith("$ "):
        acc.append("<pre>" + l + "</pre>")
        continue

      if l.lstrip().startswith("#"):
        acc.append("<pre>" + l + "</pre>")
        continue

      if l.startswith("|") or l.startswith("+"):
        acc.append("<pre>" + BLOG_PARSER.linkify(l) + "</pre>")
        continue

      # parse paragraph breaks
      if "" == l:
        acc.append("<br/>")
        continue

      l = BLOG_PARSER.linkify(l)

      # parse misc
      acc.append("<span>" + l + "</span>")

    return "".join(acc)

# end BLOG_PARSER
