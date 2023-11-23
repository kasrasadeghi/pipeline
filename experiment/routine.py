class ROUTINE:
  def get_routine_uuid():
    return "7e3e5fea-300a-4a97-ab10-ee6c687f647f.note"

  def RENDER_menu_button():
    return RENDER_UTIL.button('routine')

  def PARSE_routine_file():
    return REWRITE.note(ROUTINE.get_routine_uuid())

  def RENDER_routine_item(name):
    return f"<a class='link-button' href='javascript:void(0)'>{name}</a>"

  def RENDER_menu_page():
    note = ROUTINE.PARSE_routine_file()
    blocks = note[0]['blocks']

    acc = []
    for block in blocks:
      match block:
        case [{'line': line}]:
          match line:
            case [{'tag': routine_item}]:
              acc.append(ROUTINE.RENDER_routine_item(routine_item))
            case _:
              pass # acc.append(str({'line': line}))
        case []: # newline
          pass
        case _ as x:
          pass # acc.append(str({'block': x}))
    content = "<div class='routine-buttons'>" + "\n".join(acc) + "</div>"
    return RENDER.base_page({'title': 'Routine', 'content': content})

@app.route('/routine')
def get_routine_page():
  return ROUTINE.RENDER_menu_page()
