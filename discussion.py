class DISCUSSION:
  @classmethod
  def RENDER_MSG(cls, msg):
    try:
      msg_date = msg['children'][0]['value'].split('Date: ', 1)[1]
      msg_content = msg["value"].split("msg: ", 1)[1]
      origin = msg.get('origin', None)  # second argument of .get() is a default value
      date = util.date_cmd("-d", msg_date, "+%b %d %T")
      return (
        (f'<a href="/disc/{origin}">' if origin else "") +
        f'<div class="msg">'
        f'<div class="msg_timestamp">{date}</div>'
        f'<div class="msg_content">{escape(msg_content)}</div>'
        f'</div>' +
        (f'</a>' if origin else "")
      )
    except:
      print("ERROR: could not render msg: '" + str(msg) + "'")
      return ""
