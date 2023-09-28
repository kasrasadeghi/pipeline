@app.route('/js/<path>')
def get_js(path):
  from flask import send_from_directory
  return send_from_directory('js', path)

def link_js(path):
  return f"<script src='/js/{path}'></script>"

def include_js(path):
  with open('js/' + path) as f:
    content = f.read()
  return f"<script>" + content + "</script>"
