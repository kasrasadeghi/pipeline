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

  def content(note):
    return (
      f"<div class='msgbox'>"
      f"{RENDER.content(note)}</div>"
      f"<div class='msgbox' id='message-queue'></div>"
      f"<script src='/js/disc.js'></script>"
      f'<form onsubmit="handle_msg(event, \'{note}\')" method="post">'
        f'<input class="msg_input" autocomplete="off" autofocus type="text" name="msg">'
      f'</form>'
    )

  @staticmethod
  def MAIN(note, **kwargs):
    title = FLAT.title(note)
    bar = RENDER_UTIL.nav(f'<a href="/note/{note}">note</a>'
                          f'<a href="/edit/{note}">edit</a>')
    content = DISCUSSION_RENDER.content(note, **kwargs)

    return RENDER.base_page({'title': title, 'bar': bar, 'content': content})

  @staticmethod
  def msg(msg, **kwargs):
    msg_date = msg['date']
    date = kwargs.get('timerender', lambda msg_date: DATE.cmd("-d", msg_date, "+%T"))(msg_date)
    msg_indent = kwargs.get('msg_indent', '')

    msg_content = RENDER.line(msg['msg'])
    msg_origin = ''
    if 'origin' in msg:
      msg_origin = '/disc/' + msg['origin']

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
