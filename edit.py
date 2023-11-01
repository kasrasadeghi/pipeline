class EDIT_RENDER:
  @staticmethod
  def EDIT(**kwargs):
    title = kwargs['title']
    content = kwargs['content']
    bar = kwargs['bar']
    # compose html
    result = (
      """<script>window.addEventListener("load", () => { let el = document.getElementsByTagName("textarea")[0]; el.scrollTop = el.scrollHeight });</script>"""
      f'<form method="post" class="editor_container">'
        f'<textarea name="text" class="editor_textarea" rows="100">{content}</textarea><br/>'
        f'<input class="link-button" type="submit" value="Submit"/>'
      f'</form>'
    )
    return RENDER.base_page({'title': title, 'content': result, 'bar': bar})


@app.route("/edit/<note>", methods=['GET', 'POST'])
def route_edit(note):
  if request.method == 'POST':
    FLAT.handle_edit(note, request.form)
    return redirect(f"/edit/{note}", code=302)

  try:
    title = FLAT.title(note)
  except:
    title = "ERROR, NOTE DOESN'T HAVE METADATA"
  content = util.read_file(FLAT.to_path(note))
  bar = RENDER_UTIL.nav(f'<a href="/note/{note}">note</a>'
                        f'<a href="/disc/{note}">disc</a>')
  return EDIT_RENDER.EDIT(title=title, content=content, bar=bar)


@app.route('/config', methods=['GET', 'POST'])
def config_edit():
  if request.method == 'POST':
    FLAT.set_config(request.form)
    return redirect(f"/config", code=302)

  with open(FLAT.config_path()) as f:
    content = f.read()

  return EDIT_RENDER.EDIT(title='Edit Configuration', content=content, bar=None)
