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
              # lines without children
              case {'line': _, 'content': line}:
                block_items.append(line)
              # lines with children
              case {'indent': _, 'value': line, 'children': _, 'line': _}:
                block_items.append(line)
              case _:
                pass # block_items.append({'item': item})
          routine_menus.append(block_items)
        case _ as x:
          pass # routine_menus.append({'block': x})

    return routine_menus

  def PARSE_disc_msgs_for_tags(note_uuid):
    note = REWRITE.note(note_uuid)
    from collections import defaultdict
    tag_counts = defaultdict(int)

    # message accumulator
    msg_acc = []
    for section in note:
      if section['title'] in ('entry', 'DISCUSSION'):
        for root in section['roots']:
          for child in root['children']:
            match child:
              case {'msg': _, 'content': _, 'date': _} as msg:
                msg_acc.append(msg)

    # consider looking for substrings if they are not simple tags
    # like 'factorio planner'
    # might also work for 'READ HN' vs 'FILTER HN'
    for msg in msg_acc:
      for line_part in msg['msg']:
        match line_part:
          case {'tag': tag}:
            tag_counts[tag] += 1
          case _ as x:
            pass # LOG({'non tag part of message': x})

    return tag_counts

  def RENDER_item(name, tag_counts, tags_used):
    if name in tag_counts:
      tags_used.add(name)
      return f"<a class='link-button' href='javascript:void(0)'>{name} {tag_counts[name]}</a>"
    else:
      return f"<a class='link-button' style='color: #70e078' href='javascript:void(0)'>{name}</a>"

  def RENDER_menu_page(note):
    # add counts per routine item, for things like brushing '1/2'
    # or add separate brushes, one for morning, one for night

    tag_counts = ROUTINE.PARSE_disc_msgs_for_tags(note)
    tags_used = set()

    routine_uuid = ROUTINE.get_routine_uuid()
    routine_menus = ROUTINE.PARSE_menus_from_file(routine_uuid)
    content = '<div class="routine-menu-collection">'
    for block in routine_menus:
      content += "<div class='routine-buttons'>" + "\n".join(ROUTINE.RENDER_item(item, tag_counts, tags_used) for item in block) + "</div>"

    tags_leftover = tag_counts.keys() - tags_used
    content += "<div class='routine-buttons'>" + "\n".join(ROUTINE.RENDER_item(item, tag_counts, tags_used) for item in ['MISC', *tags_leftover]) + "</div>"
    content += "</div>"

    bar = RENDER_UTIL.nav(f'<a href="/disc/{note}">back to note</a>',
                          f'<a href="/edit/{routine_uuid}">edit routine</a>')

    return RENDER.base_page({'title': 'Routine', 'content': content, 'bar': bar})

@app.route('/routine/<note>')
def get_routine_page(note):
  return ROUTINE.RENDER_menu_page(note)
