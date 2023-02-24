class util:
  @staticmethod
  def cmd(*args, **kwargs):
    import subprocess
    return subprocess.check_output(*args, **kwargs).decode('utf8')

  @staticmethod
  def sort_mtime(files, key=lambda x: x):
    return [p[0] for p in sorted([(f, os.stat(key(f)).st_mtime) for f in files], key=lambda p: p[1])]

  @staticmethod
  def basename(filename):
    return filename.rsplit("/", 1)[1]

  @staticmethod
  def get_current_time():
    return util.date_cmd("+%a %b %e %T %Z %Y")  # from emacs/lisp/kaz.el's kaz/current-time

  @staticmethod
  def parse_time_to_utc(time):
    """
    translated from date '+%a %b %e %T %Z %Y'
    - used for comparisons and sorting
    """
    # convert the timezone to UTC because datetime in python doesn't handle timezones, omegalul
    clean_time = check_output(["date", "-d", time, "-u", "+%a %b %d %T %Z %Y"]).decode('utf8').strip()

    import datetime
    return datetime.datetime.strptime(clean_time, "%a %b %d %H:%M:%S %Z %Y")

  @staticmethod
  def date_cmd(*l):
    match l:
      case ['-d', date, output_pattern]:
        if (x := fastparse_datetime(date, l[2])):
          return x

    return check_output(["date", *l]).decode('utf8').strip()

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

  @staticmethod
  def day_before(datetime_str):
    return util.date_cmd("-d", datetime_str + " - 1 day")  # literally subtract a day, unix 'date' can do that

  @staticmethod
  def day_after(datetime_str):
    return util.date_cmd("-d", datetime_str + " + 1 day")
