_STATE = None

def clear_state():
  global _STATE
  _STATE = None

def init_state():
  global _STATE
  _STATE = dict()
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
  @classmethod
  def TEXT(R, title, content):
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
