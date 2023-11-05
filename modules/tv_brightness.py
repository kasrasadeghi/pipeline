@app.route('/event/tv_brightness_up', methods=['POST'])
def post_tv_brightness_up():
  subprocess.run('python /home/kasra/code/samsung-tv-api/main.py 1', shell=True, cwd='/home/kasra/code/samsung-tv-api/')
  return 200

@app.route('/event/tv_brightness_down', methods=['POST'])
def post_tv_brightness_down():
  subprocess.run('python /home/kasra/code/samsung-tv-api/main.py', shell=True, cwd='/home/kasra/code/samsung-tv-api/')
  return 200
