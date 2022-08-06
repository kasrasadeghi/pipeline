"""
USAGE:
def helper():
  LOG("huh")

@app.route("/example")
def get_example():
  DEBUG.init_state()

  helper()  # calls LOG, "huh" will show up in the output
  ....
  # choose one of:
  return DEBUG.DUMP(content)
  return DEBUG.TEXT(title, content)
  return Response(custom() + DEBUG.CONTENT(), 200)
"""

import time
import traceback # format_exc (for printing stacktraces)

def LOG(s):
  if DEBUG._STATE:
    DEBUG._STATE['LOG'].append(s)
  else:
    print("stateless ", end='')
  print("LOG: " + str(s))

class DEBUG:
  # TODO should make state request specific so that it can be multithreaded or multi-processed
  _STATE = None

  def clear_state():
    DEBUG._STATE = None

  def init_state():
    DEBUG._STATE = dict()
    DEBUG._STATE['start time'] = time.time()  # get current time
    DEBUG._STATE['LOG'] = list()

  def set_state(k, v):
    if DEBUG._STATE:
      LOG(f"set '{k}' to '{v}'")
      DEBUG._STATE[k] = v
    else:
      print("stateless ", end='')

  def get_state(k):
    return DEBUG._STATE[k]

  def LOG(s):
    if DEBUG._STATE:
      DEBUG._STATE['LOG'].append(s)
    else:
      print("stateless ", end='')
    print("LOG: " + str(s))

  @staticmethod
  def CONTENT():
    debug = ""
    if DEBUG._STATE is not None:
      if 'LOG' in DEBUG._STATE:
        # if log is empty, don't print anything
        if 0 == len(DEBUG._STATE['LOG']):
          return ''

        # rearrange to put the log at the end
        log = DEBUG._STATE['LOG']
        del DEBUG._STATE['LOG']
        DEBUG._STATE['LOG'] = log
      debug = f"<pre>DEBUG STATE: \n" + f"{str(escape(json.dumps(DEBUG._STATE, indent=2, default=lambda x: str(x))))}\n"
      debug += DEBUG._STATE.get("stacktrace", "")
      debug += "</pre>"
    DEBUG.clear_state()
    return debug

  # TODO add a traceback section to this
  @staticmethod
  def CATCH(exception):
    DEBUG.set_state("stacktrace", traceback.format_exc())

  @staticmethod
  def TEXT(title, content):
    debug = DEBUG.CONTENT()

    r = Response(f"<!DOCTYPE hmtl><html><head>{RENDER.STYLE()}<title>{title}</title></head>"
                 f"<body><div class=\"content\">"
                 f"<pre>{content}</pre>" +
                 debug +
                 "</div></body></html>", mimetype="text/html")
    return r

  @staticmethod
  def DUMP(content=''):
    return DEBUG.TEXT("Debug DUMP", content)

  @staticmethod
  def FILTER(debugmode):
    return debugmode and set(debugmode.split()) in []  # set to anything right now


# debug print
# TODO have a config for debugging module by module by inspecting the stacktrace
def debug(*l, **kw):
  is_debug = 'FLASK_ENV' in os.environ and os.getenv('FLASK_ENV') == 'development'

  if 'debugmode' in kw:
    debugmode = kw['debugmode']
    del kw['debugmode']
  else:
    debugmode = None

  if not DEBUG.FILTER(debugmode):
    return

  if is_debug:
    print(*l, **kw)


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
  # print('client ip:', request.remote_addr)
  # print(request.headers)
  # print(request.json)
  return Response('', 204)
