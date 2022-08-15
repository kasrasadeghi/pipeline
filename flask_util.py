# this file has wrappers around flask's "request" object
# for invocations that are not _immediately_ within the route
#
# this is to be able to better track magic dataflow

class FLASK_UTIL:
  @staticmethod
  def REFERER_NOTE():
    view, note = FLAT.try_from_url(request.environ['HTTP_REFERER'])
    return view, note

  @staticmethod
  def TELEMETRY():
    return f"""<script>
       fetch("http://{request.headers['Host']}/receive_info",
         {{ method: "POST",
            headers: {{ 'Content-Type': 'application/json'}},
            body: JSON.stringify({{width: window.screen.width, height: window.screen.height, dpr: window.devicePixelRatio }})
         }}
       )
     </script>"""

  @staticmethod
  def HOST():
    return request.headers["Host"]  # like 192.37.37.3:5000
