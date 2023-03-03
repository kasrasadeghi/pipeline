# get every parenthesized quantity
# show statistics: sum total, average (by looking for "x4" and that kind of multiple too)

@app.route('/quant/<note>')
def get_quant(note):
  import re
  entry_blocks = REWRITE.note(note)[0]['blocks']

  # only get messages that match _(_)_ and extract the middle part
  # re.search returns an optional
  acc = list()
  quants = list()
  for b in entry_blocks:
    if 'msg' in b and (x := re.search('.*\((.*)\).*', b['msg'][0])):
      quant = x.group(1)
      acc.append(quant)
      if ' x' in quant:  # "800 x4" -> (800, 4)
        value, multiplicity = map(int, quant.split(' x'))
        quants += ([value] * multiplicity)
      else:
        quants.append(int(quant))

  average = sum(quants) / len(quants) if len(quants) else 0

  content = (
    RENDER_UTIL.pre(json.dumps({'quants in msgs': acc, 'quants': quants, 'average': average, 'sum': sum(quants), 'len': len(quants)}, indent=2))
    + DISCUSSION_RENDER.content(note)
  )

  bar = RENDER_UTIL.nav(f'<a href="/note/{note}">note</a>'
                        f'<a href="/edit/{note}">edit</a>')

  # compose html
  title = FLAT.title(note)
  result = content
  return RENDER.base_page({'title': title, 'bar': bar, 'content': content})
