# this file has wrappers around flask's "request" object
# for invocations that are not _immediately_ within the route
#
# this is to be able to better track magic dataflow

class FLASK_UTIL:
  @staticmethod
  def CURRENT_URL():
    return request.path

  def CURRENT_NOTE():
    return FLAT.try_from_url(FLASK_UTIL.CURRENT_URL())

  @staticmethod
  def REFERER_NOTE():
    view, note = FLAT.try_from_url(request.environ['HTTP_REFERER'])
    return view, note

  @staticmethod
  def HEADERS():
    return request.headers

  @staticmethod
  def TELEMETRY():
    return f"""<script>
       fetch("https://{request.headers['Host']}/receive_info",
         {{ method: "POST",
            headers: {{ 'Content-Type': 'application/json'}},
            body: JSON.stringify({{width: window.screen.width, height: window.screen.height, dpr: window.devicePixelRatio }})
         }}
       )
     </script>"""

  @staticmethod
  def URL_ROOT():
    return request.url_root # like http://192.37.37.3:5000/ or https://10.50.50.2:5000

  @staticmethod
  def HOST():
    return request.headers["Host"]  # like 192.37.37.3:5000

  @staticmethod
  def ESCAPE(s):
    return str(escape(s))


@app.route("/site-map")
def site_map():
  from flask import url_for

  raw_endpoints = list()
  note_views = list()
  unmatched = list()
  for rule in app.url_map.iter_rules():
    # Filter out rules we can't navigate to in a browser
    # and rules that require parameters
    note_arg = {'note'}

    if "GET" in rule.methods:
      if len(rule.arguments) == 0:
        raw_endpoints.append(repr(rule))
      elif len(rule.arguments) == 1 and list(rule.arguments)[0] == 'note':
        note_views.append(repr(rule))
      else:
        unmatched.append((repr(rule), repr(rule.arguments)))
  return {'raw': list(reversed(raw_endpoints)), "note": note_views, "unmatched": unmatched}
