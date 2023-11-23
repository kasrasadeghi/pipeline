class ROUTINE:
  def get_routine_uuid():
    return "7e3e5fea-300a-4a97-ab10-ee6c687f647f.note"

  def RENDER_menu_button(note):
    return RENDER_UTIL.button('routine', f"/routine/{note}") # show the current number of checkmarks

  def PARSE_menus_from_file(routine_note_uuid):
    routine_note = REWRITE.note(routine_note_uuid)
    blocks = routine_note[0]['blocks']

    routine_menus = []
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
                block_items.append(line)
              case {'indent': _, 'value': line, 'children': _, 'line': _}:
                block_items.append(line)
              case _:
                pass # block_items.append({'item': item})
          routine_menus.append(block_items)
        case _ as x:
          pass # routine_menus.append({'block': x})

    return routine_menus

  def RENDER_item(name):
    return f"<a class='link-button' href='javascript:void(0)'>{name}</a>"

  def RENDER_menu_page(note):
    routine_menus = ROUTINE.PARSE_menus_from_file(ROUTINE.get_routine_uuid())
    content = '<div class="routine-menu-collection">'
    for block in routine_menus:
      content += "<div class='routine-buttons'>" + "\n".join(ROUTINE.RENDER_item(item) for item in block) + "</div>"
    content += "</div>"
    return RENDER.base_page({'title': 'Routine', 'content': content})

@app.route('/routine/<note>')
def get_routine_page(note):
  return ROUTINE.RENDER_menu_page(note)
