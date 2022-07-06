class EDIT_RENDER:
  @classmethod
  def EDIT(R, note):
    content = util.read_file(FLAT.to_path(note))

    line_height = 23;

    textarea_resize_script = """
    function textarea_resize(el) {

      // https://stackoverflow.com/questions/15195209/how-to-get-font-size-in-html
      // https://stackoverflow.com/a/15195345
      linecount = el.innerHTML.split(/\\n/).length;
      el.style.height = (""" + str(line_height * 1.065) + """ * linecount)+"px";
    }
    window.onload = () => { let el = document.getElementsByTagName("textarea")[0]; el.scrollTop = el.scrollHeight };
    """

    bar = FLAT_RENDER._bar(note,
                           f'<a href="/note/{note}">note</a>'
                           f'<a href="/disc/{note}">disc</a>'
                           )

    # compose html
    try:
      title = FLAT.title(note)
    except:
      title = "ERROR, NOTE DOESN'T HAVE METADATA"
      pass
    result = (
      f'<script>{textarea_resize_script}</script>'
      f'<form method="post">'
      #f'<textarea name="text" oninput="textarea_resize(this)" style="line-height: 23px; resize:none; overflow: auto; width: -webkit-fill-available" rows="100">{content}</textarea><br/><br/>',
        f'<textarea name="text" class="editor_textarea" rows="100">{content}</textarea><br/><br/>'
        f'<input class="link-button" type="submit" value="Submit"/>'
      f'</form>'
    )
    return RENDER.base_page(DICT(title, bar, content=result))


@app.route("/edit/<note>", methods=['GET', 'POST'])
def route_edit(note):
  if request.method == 'POST':
    FLAT.handle_edit(note, request.form)
    return redirect(f"/edit/{note}", code=302)

  return EDIT_RENDER.EDIT(note)
