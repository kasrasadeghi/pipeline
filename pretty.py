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

    match o:
      case dict():
        acc = list()
        for k, v in o.items():
          acc.append(f"{k}: {PRETTY.DUMP(v, no_symbol)}")
        if len(o.items()) == 0:
          result = '{}'
        else:
          result = symbol("{\n") + indent("\n".join(acc), color="#833") + symbol("}")

      case list():
        if len(o) == 0:
          result = "[]"
        else:
          result = symbol("[\n") \
            + indent("\n".join(PRETTY.DUMP(el, no_symbol) for el in o), color='#388') \
            + symbol("]")

      case Exception():
        import traceback
        obj = {"msg": str(o), "traceback": "\n".join(traceback.format_exception(o))}
        result = PRETTY.DUMP(obj, no_symbol)

      case str():
        if o == "\n":
          result = "\\n"
        elif o == '':
          result = '""'
        elif len(o.splitlines()) == 1:
          result = FLASK_UTIL.ESCAPE(o)
        else:
          result = '\n' + indent('"""\n' + FLASK_UTIL.ESCAPE(o) + '"""')

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

  return RENDER.base_page({'title': "PRETTY.DUMP",
                           'content': '<pre style="font-feature-settings: \"liga\" 0">' + PRETTY.DUMP(obj) + "</pre>"})
