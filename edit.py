class EDIT_RENDER:
  @classmethod
  def EDIT(R, note):
    content = util.read_file(FLAT.to_path(note))

    bar = RENDER_UTIL.nav(f'<a href="/note/{note}">note</a>'
                          f'<a href="/disc/{note}">disc</a>')

    # compose html
    try:
      title = FLAT.title(note)
    except:
      title = "ERROR, NOTE DOESN'T HAVE METADATA"
      pass
    result = (
      f'<form method="post">'
        f'<textarea name="text" class="editor_textarea" rows="100">{content}</textarea><br/><br/>'
        f'<input class="link-button" type="submit" value="Submit"/>'
      f'</form>'
    )
    return RENDER.base_page({'title': title, 'content': result, 'bar': bar})


@app.route("/edit/<note>", methods=['GET', 'POST'])
def route_edit(note):
  if request.method == 'POST':
    FLAT.handle_edit(note, request.form)
    return redirect(f"/edit/{note}", code=302)

  return EDIT_RENDER.EDIT(note)
