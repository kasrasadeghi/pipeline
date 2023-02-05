@app.route('/js/<path>')
def get_js(path):
  from flask import send_from_directory
  return send_from_directory('js', path)
