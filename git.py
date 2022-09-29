class GIT_HANDLE:
  @classmethod
  def _add(cls, note):
    if FLAT.exists(note):
      FLAT.cmd(['git', 'add', note]).strip()
      return redirect(f"/git/diff-staged/{note}", code=302)

    else:
      LOG(f"ERROR: note '{note}' doesn't exist to 'git add'")
      return Response('', 204)

  @classmethod
  def _unstage(cls, note):
    if FLAT.exists(note):
      FLAT.cmd(['git', 'restore', '--staged', note]).strip()
      return redirect(f"/git/diff/{note}")

    else:
      LOG(f"ERROR: note '{note}' doesn't exist to 'git add'")
      return Response('', 204)

  @classmethod
  def _commit(cls, message):
    stage_size = len(FLAT.cmd(['git', 'diff', '--staged']).strip())

    # if we have something staged, commit it and redirect to showing that commit
    if stage_size != 0:
      FLAT.cmd(['git', 'commit', '-m', message]).strip()
      just_committed = FLAT.cmd(['git', 'rev-parse', 'HEAD']).strip()
      return redirect("/git/show/" + just_committed)

    # if we have nothing staged, then show the log
    return redirect("/git/log")

# END HANDLE

# RENDER
class GIT:
  @classmethod
  def _git_porcelain(R):
    status = FLAT.cmd(['git', 'status', '--porcelain'])  # NO .strip() !

    acc = list()

    for l in status.splitlines():
      if (i := l.rfind(".note")) != -1 and '/' not in l:
        before, uuid = l[:3], l[3:]  # 3 is the length of the annotation that git porcelain gives us
        acc.append((before, uuid, "uuid"))

    def comparable_date(p):
      return util.parse_time_to_utc(FLAT.metadata(p[1])['Date'])

    acc_sorted = list(reversed(sorted(acc, key=comparable_date)))

    # gather the non-uuid notes (for example in raw/)
    for l in status.splitlines():
      if l.rfind(".note") == -1 or '/' in l:
        before, filename = l[:3], l[3:]
        acc_sorted.append((before, filename, "non-uuid"))

    acc = list()
    acc_untracked = list()
    for (before, filename, is_uuid) in acc_sorted:
      filename_repr = f'<a href="{FLAT.to_url(filename, view="disc")}">{FLAT.title(filename)}</a>' \
        if is_uuid == 'uuid' else filename

      if '??' in before:
        el = (
          before +
          f'<form style="display:inline" "action="/git" method="post">'
          f'<button class="link-button" name="add" value="{filename}">add</button> '
          f'</form>' +
          filename_repr
        )
        acc_untracked.append(el)

      else:
        el = (
          before +
          f'<a href="/git/diff/{filename}">work</a> '
          f'<form style="display:inline "action="/git" method="post">'
          f'<button class="link-button" name="unstage" value="{filename}">{str(escape("<"))}unstage</button> '
          f'<button class="link-button" name="add" value="{filename}">add{str(escape(">"))}</button> '
          f'</form>'
          f'<a href="/git/diff-staged/{filename}">stage</a>   ' +
          filename_repr
        )
        acc.append(el)

    status = "\n".join(acc_untracked + acc)

    return status

  @classmethod
  def _git_status(R):
    status = FLAT.cmd(['git', 'status']).strip()

    UUID_LEN = len("2e62fd14-9b3a-4275-9a39-7bf3d6b488c7.note")

    acc = list()
    for l in status.splitlines():
      if (i := l.rfind(".note")) != -1:
        before, uuid = l[:-UUID_LEN], l[-UUID_LEN:]
        acc.append(before + f'<a href="/note/{uuid}">{FLAT.title(uuid)}</a>')
      else:
        acc.append(str(escape(l)))
    status = "\n".join(acc)

    return status

  @classmethod
  def _git_diff_single(R, note):
    """the diff between working and stage"""
    diff = FLAT.cmd(['git', '-c', 'color.ui=always', 'diff', note]).strip()
    diff = RENDER_UTIL._parse_color(str(escape(diff)))
    return diff

  @classmethod
  def _git_diff_staged(R, note):
    """the diff between stage and head"""
    diff = FLAT.cmd(['git', '-c', 'color.ui=always', 'diff', '--staged', note]).strip()
    diff = RENDER_UTIL._parse_color(str(escape(diff)))
    return diff

  @classmethod
  def _git_diff(R):
    """the diff between work and stage"""
    # git color always: https://stackoverflow.com/questions/16073708/force-git-status-to-output-color-on-the-terminal-inside-a-script
    diff = FLAT.cmd(['git', '-c', 'color.ui=always', 'diff']).strip()
    diff = RENDER_UTIL._parse_color(str(escape(diff)))
    return diff

  @classmethod
  def _git_stage(R):
    """show the stage as the diff between it and HEAD"""
    diff = FLAT.cmd(['git', '-c', 'color.ui=always', 'diff', '--staged']).strip()
    diff = RENDER_UTIL._parse_color(str(escape(diff)))
    return diff

  @classmethod
  def _git_log(R):
    diff = FLAT.cmd(['git', '-c', 'color.ui=always', '--no-pager', 'log', '--decorate=short'])

    # add links for every commit
    prefix = RENDER_UTIL.ANSI() + "33m" + "commit "
    len_prefix = len(prefix)
    len_sha = len("da365d2d6a9c6c7dc5a748d382eab0434f20c04c")
    sha_start = len_prefix
    sha_end = sha_start + len_sha
    acc = list()
    for L in diff.splitlines():
      if L.startswith(prefix):
        pre, sha, post = str(escape(L[:sha_start])), str(escape(L[sha_start:sha_end])), str(escape(L[sha_end:]))
        LOG({"git log": sha})
        acc.append(pre + f'<a href="/git/show/{sha}">{sha}</a>' +post)
      else:
        acc.append(str(escape(L)))

    diff = "\n".join(acc)
    diff = RENDER_UTIL._parse_color(diff)

    return diff

  @classmethod
  def _git_show_commit(R, sha):
    output = FLAT.cmd(['git', '-c', 'color.ui=always', 'show', sha])
    output = RENDER_UTIL._parse_color(str(escape(output)))
    return output

  @classmethod
  def _git_menu(R):
    menu = R._git_porcelain()
    return f'<pre><h1>$ <a href="/git/menu">git status --porcelain</a></h1>{menu}</pre>'

  @classmethod
  def _cmd(R, cmd, output):
    return f"<pre><h1>$ {cmd}</h1>{output}</pre>"

  @staticmethod
  def base_page(title, content):
    return

  @classmethod
  def RENDER_GIT(R):
    title = "Git Status"

    status = R._git_status()
    diff = R._git_diff()
    untracked_filenames = FLAT.cmd(["git", "ls-files", "--others", "--exclude-standard"]).strip()

    untracked_files = list()
    for l in untracked_filenames.splitlines():
      with open(FLAT.to_path(l)) as f:
        untracked_files.append(f.read())
      untracked_files[-1] = ('<span style="font-weight: bold">' + str(escape(l)) + "</span>\n" +
                             '<span style="color: green">' + str(escape(untracked_files[-1])) + "</span>\n")
    untracked = "".join(untracked_files)

    content = (R._cmd("git status", status) +
               RENDER_UTIL.bar() +
               R._cmd("git diff", diff) +
               RENDER_UTIL.bar() +
               f'<pre><h1>UNTRACKED FILES</h1>\n{untracked}</pre>')

    return RENDER.base_page(DICT(title, content, bar=None))

  @classmethod
  def RENDER_GIT_MENU(R):
    title = "Git Menu"

    content = (
      R._git_menu() +
      '<div style="margin-top: 8px">'
      f'<a href="/git" class="link-button">overview</a>' +
      f'<a href="/git/stage" class="link-button">stage</a>' +
      f'<a href="/git/log" class="link-button">log</a>' +
      "</div>"
    )

    return RENDER.base_page(DICT(title, content, bar=None))

  @classmethod
  def RENDER_GIT_DIFF(R, filename, staged):
    is_uuid = not ('/' in filename or not filename.endswith('.note'))
    filename_title = (FLAT.title(filename) if is_uuid else filename)
    title = "Git Diff: " + filename_title

    if staged:
      flag = ' --staged'
      output = R._git_diff_staged(filename)
    else:
      flag = ' '
      output = R._git_diff_single(filename)

    content = (
      R._git_menu() +
      RENDER_UTIL.bar() +
      R._cmd(f"git diff{flag} '{filename_title}'", output)
    )

    return RENDER.base_page(DICT(title, content, bar=None))

  @classmethod
  def RENDER_GIT_STAGE(R):
    title = "Git Stage"
    content = (
      R._git_menu() +
      RENDER_UTIL.bar() +
      f'<a href="/git/commit" class="link-button">commit</a>' +
      R._cmd("git diff --staged", R._git_stage())
    )

    return RENDER.base_page(DICT(title, content, bar=None))

  @classmethod
  def RENDER_GIT_COMMIT(R, message=None):
    title = "Git Commit"

    output = R._git_stage()

    default_value = " value=\"" + message + "\"" if message else ""
    content = (
      f'<form method="post"><input class="msg_input" autocomplete="off" ' +
        f'autofocus type="text" name="commit_message"{default_value}>' +
      '</form>' +
      R._cmd("git diff --staged", output))

    return RENDER.base_page(DICT(title, content, bar=None))


  @classmethod
  def RENDER_GIT_SHOW(R, sha):
    """the @param sha is the specific sha of the commit you want to render"""
    title = "Git Commit"

    output = R._git_show_commit(sha)

    content = (
      R._cmd("git show", output))

    return RENDER.base_page(DICT(title, content, bar=None))

  @classmethod
  def RENDER_GIT_LOG(R):
    title = "Git Log"

    log = R._git_log()

    content = (
      R._git_menu() +
      R._cmd("git log", log))

    return RENDER.base_page(DICT(title, content, bar=None))

  # END RENDER

# ROUTES

@app.route("/git/commit", methods=['GET', 'POST'])
def git_commit():
  if 'POST' == request.method:
    if 'commit_message' in request.form:
      return GIT_HANDLE._commit(request.form['commit_message'])

    LOG("ERROR: unhandled request with form: ")
    LOG(request.form)
    return Response('', 204)

  message = None
  if 'message' in request.args:
    message = request.args['message']

  return GIT.RENDER_GIT_COMMIT(message)

@app.route("/git/show/<sha>")
def git_show_commit(sha):
  return GIT.RENDER_GIT_SHOW(sha)

@app.route("/git", methods=['GET', 'POST'])
def git_status():
  if 'POST' == request.method:
    if 'add' in request.form:
      return GIT_HANDLE._add(request.form['add'])

    if 'unstage' in request.form:
      return GIT_HANDLE._unstage(request.form['unstage'])

    LOG("ERROR: unhandled request with form: ")
    LOG(request.form)
    return Response('', 204)

  return GIT.RENDER_GIT()

@app.route("/git/log")
def git_log():
  return GIT.RENDER_GIT_LOG()

@app.route("/git/stage")
def git_stage():
  return GIT.RENDER_GIT_STAGE()

@app.route("/git/menu")
def git_menu():
  return GIT.RENDER_GIT_MENU()

@app.route("/git/diff/<path:filename>")
def git_diff(filename):
  return GIT.RENDER_GIT_DIFF(filename, staged=False)

@app.route("/git/diff-staged/<path:filename>")
def git_diff_staged(filename):
  return GIT.RENDER_GIT_DIFF(filename, staged=True)

# END ROUTES
