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

      if len(b) == 2 and b[0].startswith('left: ') and b[1].startswith('right: '):
        acc.append('<span style="color:red">' + str(b) + "</span><br/>")
        speakers = dict()
        speakers['left'] = b[0].removeprefix('left: ').split(', ')
        speakers['right'] = b[1].removeprefix('right: ').split(', ')
        continue

      for l in b:
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
          if isinstance(l, str): # TODO render "dict()" as well or just put this into /disc/ mode
            acc.append("&nbsp;&nbsp;" + l + "<br/>")

    return "\n".join(acc)

  rendered_page = RENDER.page(
    note,
    PARSER.parse_file(FLAT.to_path(note)),
    render_section=section
  )

  return RENDER.base_page(
    {'title': 'testing blog render for FBCONV ' + note,
     'content': rendered_page})
