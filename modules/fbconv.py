@app.route('/test/fbconv/<note>')
def test_fbconv(note):

  speakers = None
  def section(s, **kwargs):
    if s['title'] != 'FBCONV':
      return RENDER.section(s, **CONTEXT.DEFAULT(kwargs, 'render_section'))

    acc = list()
    for b in s['blocks']:
      if TREE.is_newline(b):
        continue

      if len(b) == 2 and b[0]['line'][0].startswith('left: ') and b[1]['line'][0].startswith('right: '):
        acc.append('<span style="color:red">' + str(b) + "</span><br/>")
        speakers = dict()
        speakers['left'] = b[0]['line'][0].removeprefix('left: ').split(', ')
        speakers['right'] = b[1]['line'][0].removeprefix('right: ').split(', ')
        continue

      for line in b:
        l = line['line'][0]
        if speakers:
          if l in speakers['left']:
            if not speakers.get('current', None) == 'left':
              speakers['current'] = 'left'
              acc.append('<span style="color:#f88">' + str(l) + "</span><br/>")
            continue
          if l in speakers['right']:
            if not speakers.get('current', None) == 'right':
              speakers['current'] = 'right'
              acc.append('<span style="color:#88f">' + str(l) + "</span><br/>")
            continue
          acc.append("&nbsp;&nbsp;" + str(l) + "<br/>")

    return "\n".join(acc)

  rendered_page = RENDER.content(note, render_section=section)

  return RENDER.base_page(
    {'title': 'testing blog render for FBCONV ' + note,
     'content': rendered_page})
