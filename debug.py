import time
import traceback # format_exc (for printing stacktraces)

# convenience function
def LOG(s):
  DEBUG.LOG(s)

class DEBUG:
  _GLOBAL_LOG = []
  _GLOBAL_LOG_ENABLED = False

  @staticmethod
  def frameinfo(frame):
    return {
      "filename": frame.f_code.co_filename,
      "funcname": frame.f_code.co_name,
      "line": frame.f_lineno
    }

  @staticmethod
  def first_nondebug_frame(predicate=None):
    # find the first frame not from "debug.py" that also passes an optional predicate
    import inspect
    def check(frame):
      nonlocal predicate
      if predicate:
        return predicate(frame)
      return False

    parent_frame = inspect.currentframe()
    while parent_frame.f_code.co_filename == "debug.py" or check(parent_frame):
      parent_frame = parent_frame.f_back

    return parent_frame

  @staticmethod
  def LOG(s):
    if 'DEBUG_STATE' in g:
      g.DEBUG_STATE['LOG'].append(s)
    if DEBUG._GLOBAL_LOG_ENABLED:
      parent_frame = DEBUG.first_nondebug_frame(lambda f: f.f_code.co_name == 'LOG')
      DEBUG._GLOBAL_LOG.append({"i": len(DEBUG._GLOBAL_LOG), "frame": DEBUG.frameinfo(parent_frame), "content": s})

  @staticmethod
  def RENDER_LOG():
    def render_log_entry(entry):
      result = (
        "<div style='border-top: 1px white solid; margin: 2px'>"
          "<div>"
            "<span class='mono' style='color: #aaa'>"
            f"#{entry['i']} "
            f"line {entry['frame']['line']} "
            f"{entry['frame']['filename']} "
            f"{entry['frame']['funcname']}"
            "</span>"
          "</div>"
          "<div>" +
            "<pre>" + PRETTY.DUMP(entry['content']) + "</pre>"
          + "</div>"
        "</div>"
      )
      return result

    content = (
      f'<form style="display:inline" method="post">'
        f'<button class="link-button" name="clear" value="debuglog">clear</button> '
        f'<button class="link-button" name="disable" value="debuglog">disable</button> '
      f'</form>'
      f"<pre>DEBUG LOG: \n</pre>" + "".join(map(render_log_entry, DEBUG._GLOBAL_LOG))
    )
    return RENDER.base_page({'content': content, 'title': "DEBUG LOG"})

  @staticmethod
  def TEXT(title, content):
    r = Response(f"<!DOCTYPE hmtl><html><head>{RENDER_UTIL.STYLE()}<title>{title}</title></head>"
                 f"<body><div class=\"content\">"
                 f"<pre>{content}</pre>" +
                 "</div></body></html>", mimetype="text/html")
    return r

@app.route("/debuginfo")
def route_debuginfo():
  jsondump = lambda data: json.dumps(data, default=lambda x: str(x), indent=2)

  return (
    f"<h1>client ip:</h1><pre>{request.remote_addr}</pre>"
    f"<h1>request.environ:</h1><pre>{jsondump(request.environ)}</pre>"
    f"<h1>request headers:</h1><pre>{request.headers}</pre>"
  )

@app.route("/receive_info", methods=['POST'])
def receive_info():
  # LOG({'client ip': request.remote_addr})
  # LOG({'headers': dict(request.headers)})
  # LOG({'params/args': dict(request.args)})
  return Response('', 204)


@app.route("/debuglog", methods=['GET', 'POST'])
def get_debuglog():
  DEBUG._GLOBAL_LOG_ENABLED = True
  if request.method == 'POST':
    if 'clear' in request.form:
      DEBUG.clear_log()
      return redirect('/debuglog')
    if 'disable' in request.form:
      DEBUG._GLOBAL_LOG_ENABLED = False
      DEBUG.clear_log()
      return redirect('/today')
  return DEBUG.RENDER_LOG()

@app.route("/debuglog/clear")
def clear_debuglog():
  DEBUG._GLOBAL_LOG_ENABLED = False
  DEBUG.clear_log()
  return redirect('/debuglog')

@app.route("/debug/headers")
def debug_headers():
  headers = dict(request.headers)
  acc = [f"{k}: {v}" for k, v in headers.items()]
  acc.append("---")
  acc.append("request.remote_addr: " + request.remote_addr)
  acc.append("request.path: " + request.path)
  acc.append("request.url: " + request.url)
  acc.append("request.base_url: " + request.base_url)
  acc.append("request.url_root: " + request.url_root)
  content = "<pre>" + FLASK_UTIL.ESCAPE(str('\n'.join(acc))) + "</pre>"
  title = "request headers"
  return RENDER.base_page({'title': title, 'content': content})
