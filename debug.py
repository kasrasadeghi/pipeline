import time

# TODO should make state request specific so that it can be multithreaded or multi-processed
_STATE = None

def clear_state():
  global _STATE
  _STATE = None

def init_state():
  global _STATE
  _STATE = dict()
  _STATE['start time'] = time.time()  # get current time
  _STATE['LOG'] = list()

def set_state(k, v):
  LOG(f"set '{k}' to '{v}'")
  _STATE[k] = v

def get_state(k):
  return _STATE[k]

def LOG(s):
  _STATE['LOG'].append(s)
  print("LOG: " + str(s))

class DEBUG:
  @staticmethod
  def TEXT(title, content):
    debug = ""
    if _STATE is not None:
      if 'LOG' in _STATE:
        # rearrange to put the log at the end
        log = _STATE['LOG']
        del _STATE['LOG']
        _STATE['LOG'] = log
      debug = f"<pre>DEBUG STATE: \n" + f"{json.dumps(_STATE, indent=2)}</pre>"

    r = Response(f"<!DOCTYPE hmtl><html><head>{RENDER.STYLE()}<title>{title}</title></head>"
                 f"<body><div class=\"content\">"
                 f"<pre>{content}</pre>" +
                 debug +
                 "</div></body></html>", mimetype="text/html")
    clear_state()
    return r

  @staticmethod
  def FILTER(debugmode):
    return debugmode and set(debugmode.split()) in []


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
