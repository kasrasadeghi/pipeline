class util:
  @staticmethod
  def cmd(*args, **kwargs):
    import subprocess
    kwargs |= {'stdout': subprocess.PIPE}
    p = subprocess.run(args, **kwargs)
    assert p.returncode == 0, f'{repr(p)}'
    return p.stdout.decode('utf8')

  @staticmethod
  def sort_mtime(files, cwd='./'):
    return [p[0] for p in sorted([(f, os.stat(os.path.join(cwd, f)).st_mtime) for f in files], key=lambda p: p[1])]

  @staticmethod
  def basename(filename):
    return filename.rsplit("/", 1)[1]

  @classmethod
  def read_file(R, filepath):

    if not os.path.isfile(filepath):
      LOG(f"ERROR: reading file that does not exist: '{filepath}'")
      return ""

    acc = list()

    with open(filepath) as f:
      c = f.read()
      if not c.endswith("\n"):
        acc.append("\n")
      acc.append(c)
    return "".join(acc)
