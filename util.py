class util:
  @staticmethod
  def cmd(*args, **kwargs):
    import subprocess
    return subprocess.check_output(*args, **kwargs).decode('utf8')

  @classmethod
  def sort_recent(_, files, root_path):
    return [p[0] for p in sorted([(f, os.stat(root_path +'/'+ f).st_mtime) for f in files], key = lambda p: p[1])]

  @classmethod
  def basename(_, filename):
    return filename.rsplit("/", 1)[1]

  @classmethod
  def get_current_time(_):
    datecmd=["date", "+%a %b %e %T %Z %Y"]  # from emacs/lisp/kaz.el's kaz/current-time
    return check_output(datecmd).decode('latin-1')

  @classmethod
  def parse_time_to_utc(_, time):
    """
    translated from date '+%a %b %e %T %Z %Y'
    - used for comparisons and sorting
    """
    # convert the timezone to UTC because datetime in python doesn't handle timezones, omegalul
    clean_time = check_output(["date", "-d", time, "-u", "+%a %b %d %T %Z %Y"]).decode('utf8').strip()
    return datetime.datetime.strptime(clean_time, "%a %b %d %H:%M:%S %Z %Y")

  @classmethod
  def date_cmd(_, *l):
    return check_output(["date", *l]).decode('utf8').strip()

  @classmethod
  def read_file(R, filepath):

    if not os.path.isfile(filepath):
      print(f"ERROR: reading file that does not exist: '{filepath}'")
      return ""

    acc = list()

    with open(filepath) as f:
      c = f.read()
      if not c.endswith("\n"):
        acc.append("\n")
      acc.append(c)
    return "".join(acc)

  @staticmethod
  def day_before(datetime_str):
    return util.date_cmd("-d", datetime_str + " - 1 day")  # literally subtract a day, unix 'date' can do that

  @staticmethod
  def day_after(datetime_str):
    return util.date_cmd("-d", datetime_str + " + 1 day")
