class DISCUSSION:
  @staticmethod
  def is_msg(item):
    """ checks whether an item in a block is a msg """
    if not isinstance(item, dict):
      LOG({"ERROR: cannot check a non-dictionary:", item})
      return False
    return 'msg' in item and 'date' in item

  def date(msg):
    if not 'children' in msg:
      LOG({'ERROR': msg})
    if isinstance(msg, list):
      LOG({'ERROR': 'msg cannot be list, you\'re probably passing in a block', 'msg': msg})
    return msg['children'][0]['value'].removeprefix('Date: ')

# end DISCUSSION


class DISCUSSION_RENDER:
  def textfield(note, **kwargs):
    textfield = (f"<div class='action-menu'>"
        "<div class='sidebar-buttons'>"
        f"<a class='link-button' href='javascript:void()' onclick='paste(); return false;'>paste</a>"
        f"<a class='link-button' href='javascript:void()' onclick='clearInput(); return false;'>clear</a>"
        "</div>"
        f'<form style="margin:0" onsubmit="handle_msg(event, \'{note}\')" method="post">'
          f'<input id="msg_input" class="msg_input" autocomplete="off" autofocus type="text" name="msg">'
        f'</form>'
        "</div>"
        """<script>
        async function paste() {
          let x = await navigator.clipboard.readText();
          document.getElementById('msg_input').value += x;
        }
        function clearInput() { document.getElementById('msg_input').value = ''; }
        navigator.permissions.query({ name: 'clipboard-read' });
        </script>""")
    return textfield

  def content(note, **kwargs):
    return (
      f"<div id='discussion_messages'>"
        f"<div class='msglist'>"
        f"{RENDER.content(note)}</div>"
        f"<div class='msglist' id='message-queue'></div>"
        """<script>
          const scrollingElement = document.getElementById('main');
          scrollingElement.scrollTop = scrollingElement.scrollHeight;
        </script>"""
      f"</div>"
    )

  @staticmethod
  def MAIN(note, **kwargs):
    title = FLAT.title(note)
    bar = RENDER_UTIL.nav(f'<a href="/note/{note}">note</a>'
                          f'<a href="/edit/{note}">edit</a>')
    content = DISCUSSION_RENDER.content(note, **kwargs)
    textfield = DISCUSSION_RENDER.textfield(note, **kwargs)

    return RENDER.base_page({'title': title, 'bar': bar, 'content': content, 'footer': textfield})

  @staticmethod
  def msg(msg, **kwargs):
    msg_date = msg['date']
    date = kwargs.get('timerender', lambda msg_date: DATE.cmd("-d", msg_date, "+%T"))(msg_date)

    msg_origin = ''
    if 'origin' in msg:
      msg_origin = '/disc/' + msg['origin']
      if 'origin_note' not in kwargs:
        kwargs['origin_note'] = msg['origin']
    elif 'origin_note' in kwargs:
      msg_origin = '/disc/' + kwargs['origin_note']

    msg_content = RENDER.line(msg['msg'], **kwargs)
    msg_indent = ''
    if msg_content.startswith('- '):
      msg_indent = "<span class='msg_dash'><b>-</b></span>"
      msg_content = msg_content.removeprefix('- ')

    return (
      f'<div id="{msg_date}" class="msg">'
      f'<a class="msg_timestamp" href="{msg_origin}#{msg_date}">{date}</a>'
      f'<div class="msg_container">{msg_indent}<div class="msg_content">{msg_content}</div></div>'
      # f'<div>{str(TAG.gather(msg["content"]))}</div>'
      f'</div>'
    )

# end DISCUSSION_RENDER


@app.route("/disc/<note>", methods=["GET", "POST"])
def get_disc(note):
  # handle messages
  if request.method == 'POST':
    unhandled, result_url = COMMAND.PARSE(note, request.form['msg'])
    LOG({'unhandled': unhandled, 'result_url': result_url, 'commands': COMMAND.handlers})
    if unhandled:
      FLAT.handle_msg(note, request.form)
    if result_url:
      return redirect(result_url)
    return redirect(FLAT.to_url(note, view='disc'))

  # default case: handle rendering
  return DISCUSSION_RENDER.MAIN(note)

@app.route('/huh')
def get_huh():
  return """
  <style>
body {
  margin: 0;
}
footer {
  background: red;
  width: 100%;
  height: 100px;
  position: absolute; bottom: 0; left: 0;
}
header {
  height: 100px;
  width: 100%;
  background: blue;
  position: absolute; top: 0; left: 0;
}
main {
  height: calc(100dvh - 100px/*top*/ - 100px/*bottom*/ - 20px/*2x padding*/);
  margin-top: 100px;
  margin-bottom: 100px;
  padding: 10px;
  background: purple;
  overflow-y: scroll;
}
#msgbox {
  margin: 5px;
  width: -webkit-fill-available;
}
button {
  margin: 5px;
}
</style>
<body>
  <header><h1>title</h1></header>
  <main>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p> huh </p>
    <p style='margin: 0'> huh </p>
  </main>
  <footer>
    <button>huh</button>
    <form method="post">
      <input id="msgbox" autocomplete="off" autofocus type="text" name="msg">
    </form>
  </footer>
</body>"""
