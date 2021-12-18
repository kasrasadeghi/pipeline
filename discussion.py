class DISCUSSION:
  @classmethod
  def RENDER_MSG(cls, msg):
    try:
      msg_date = msg['children'][0]['value'].split('Date: ', 1)[1]
      msg_content = msg["value"].split("msg: ", 1)[1]
      date = util.date_cmd("-d", msg_date, "+%b %d %T")
      return f'<div class="msg"><div class="msg_timestamp">{date}</div><div class="msg_content">{escape(msg_content)}</div></div>'
    except:
      print("ERROR: could not render msg: '" + str(msg) + "'")
      return ""
