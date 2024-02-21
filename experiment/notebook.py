@app.route('/notebook/<name>')
def get_notebook(name):
  from urllib.parse import unquote_plus
  name = unquote_plus(name)
  notes_with_name = [x for x in FLAT.list_by_mtime() if name in FLAT.title(x)]


  toggle_all = """
    <button onclick='toggle_all_collapses()'>Toggle All</button>
    <script>
      function toggle_all_collapses() {
        let all = [...document.getElementsByTagName('details')];
        let should_open = all.some(x => !x.open);
        for (let x of all) {
          x.open = should_open;
        }
      }
    </script>
  """
  acc = [toggle_all]
  for note in notes_with_name:
    content = RENDER.content(note)
    show = RENDER_UTIL.banner(f"<a href='{FLAT.to_url(note, view='disc')}'>" + FLAT.title(note) + "</a>")
    acc.append(RENDER_UTIL.collapse(show=show, content=content))
  return RENDER.base_page({'title': f"Notebook '{name}'", 'content': '\n'.join(acc)})