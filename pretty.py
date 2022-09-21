# i tried using pprint and json.dumps, but both of them gave bad results
# - pprint was very deep and nested, json.dumps didn't allow for multiline strings

class PRETTY:
  @staticmethod
  def DUMP(o, no_symbol=False):
    import pprint

    result = None
    indent_str = "  "
    def indent(s, color="#111"):
      #return s
      return "".join(map(lambda l: f'<span style="background: {color}"> </span> ' + l + "\n", s.splitlines()))

    def symbol(s):
      nonlocal no_symbol
      if no_symbol:
        return ""
      else:
        return s

    if isinstance(o, dict):
      acc = list()
      for k, v in o.items():
        acc.append(f"{k}: {PRETTY.DUMP(v, no_symbol)}")
      if len(o.items()) == 0:
        result = '{}'
      else:
        result = symbol("{\n") + indent("\n".join(acc), color="#833") + symbol("}")

    if isinstance(o, list):
      if len(o) == 0:
        result = "[]"
      else:
        acc = list()
        for el in o:
          acc.append(PRETTY.DUMP(el, no_symbol))
        result = symbol("[\n") + indent("\n".join(acc), color='#388') + symbol("]")

    if isinstance(o, Exception):
      import traceback
      obj = {"msg": str(o), "traceback": "\n".join(traceback.format_exception(o))}
      result = PRETTY.DUMP(obj, no_symbol)

    if isinstance(o, str):
      if o == "\n":
        result = "\\n"
      elif o == '':
        result = '""'
      elif len(o.splitlines()) == 1:
        result = str(escape(o))
      else:
        result = '\n' + indent('"""\n' + str(escape(o)) + '"""')

    if result is None:
      result = repr(o)

    return result


@app.route('/test/pretty')
def test_pretty():
  obj = {
    "frame": {
      "filename": 'debug.py',
      "funcname": 'LOG',
      "line": 93
    },
    "content": {
      "ERROR could not render msg": {
        "indent": 0,
        "value": 'msg: awaken 0800',
        "children": [
          {
            "indent": 1,
            "value": 'Date: Sun Aug 14 08:02:36 PDT 2022',
            "children": []
          }
        ]
      },
      "exception": TypeError("'dict' object is not callable")
    }
  }

  return RENDER.base_page(DICT(title="PRETTY.DUMP", bar=None, content='<pre style="font-feature-settings: \"liga\" 0">' + PRETTY.DUMP(obj) + "</pre>"))
