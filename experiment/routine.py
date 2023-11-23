class ROUTINE:
  def get_routine_uuid():
    return "7e3e5fea-300a-4a97-ab10-ee6c687f647f.note"

  def RENDER_menu_button():
    return RENDER_UTIL.button('routine')

  def PARSE_routine_file():
    return REWRITE.note(ROUTINE.get_routine_uuid())

  def RENDER_routine_item(name):
    # return f"<a class='link-button' href='javascript:void(0)'>{name}</a>"
    return PRETTY.DUMP(name)

  def RENDER_menu_page():
    note = ROUTINE.PARSE_routine_file()
    blocks = note[0]['blocks']

    acc = []
    for block in blocks:
      match block:
        case []: # newline
          pass
        case [{'line': _, 'content': '---'}]:
          break # on ---
        case [*items]:
          block_items = []
          for item in items:
            match item:
              case {'line': _, 'content': line}:
                block_items.append({'routine-item': line})
              case {'indent': _, 'value': line, 'children': _, 'line': _}:
                block_items.append({'routine-item': line})
              case _:
                block_items.append({'item': item})
          acc.append(block_items)
        case _ as x:
          acc.append({'block': x})
    # content = "<div class='routine-buttons'>" + "\n".join(acc) + "</div>"
    content = "<pre>" + PRETTY.DUMP(acc) + "</pre>"
    return RENDER.base_page({'title': 'Routine', 'content': content})

@app.route('/routine')
def get_routine_page():
  return ROUTINE.RENDER_menu_page()
