# show lines of code for the project, separating the modules and tools folders

@app.route("/loc")
def get_loc():
  core_loc = "core:\n" + util.cmd("tokei", "-f", '-s', 'code', '-e', 'modules', '-e', 'tools')
  modules_loc = "\n\nmodules:\n" + util.cmd("tokei", "-f", '-s', 'code', cwd='modules')
  tools_loc = "\n\ntools:\n" + util.cmd("tokei", "-f", '-s', 'code', cwd='tools')
  return RENDER.base_page({'title': 'Lines of Code', 'content': RENDER_UTIL.pre(core_loc + modules_loc + tools_loc)})
