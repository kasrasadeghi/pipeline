# depends on pattern.py

class DATE:

  @staticmethod
  def cmd(*l):
    match l:
      case ['-d', date, output_pattern]:
        if (x := DATE.fastparse_datetime(date, l[2])):
          return x

    return util.cmd("date", *l).strip()

  @staticmethod
  def pattern():
    return "+%a %b %e %T %Z %Y"

  @staticmethod
  def now():
    return DATE.cmd(DATE.pattern())  # looks like: Tue Feb 04 20:59:49 PST 2023

  @staticmethod
  def day_before(datetime_str):
    return DATE.cmd("-d", datetime_str + " - 1 day", DATE.pattern())  # literally subtract a day, unix 'date' can do that

  @staticmethod
  def day_after(datetime_str):
    return DATE.cmd("-d", datetime_str + " + 1 day", DATE.pattern())

  @staticmethod
  def parse_time_to_utc(time):
    """
    translated from date '+%a %b %e %T %Z %Y'
    - used for comparisons and sorting
    """
    # convert the timezone to UTC because datetime in python doesn't handle timezones
    clean_time = check_output(["date", "-d", time, "-u", "+%a %b %d %T %Z %Y"]).decode('utf8').strip()

    import datetime
    return datetime.datetime.strptime(clean_time, "%a %b %d %H:%M:%S %Z %Y")


# a set of functions that help avoid calling unix date
  @staticmethod
  def abbr_month_to_full(x):
    return {
      'Jan': 'January',
      'Feb': 'February',
      'Mar': 'March',
      'Apr': 'April',
      'May': 'May',
      'Jun': 'June',
      'Jul': 'July',
      'Aug': 'August',
      'Sep': 'September',
      'Oct': 'October',
      'Nov': 'November',
      'Dec': 'December'
    }[x]

  @staticmethod
  def full_month_to_abbr(x):
    return {
      'January'  : 'Jan',
      'February' : 'Feb',
      'March'    : 'Mar',
      'April'    : 'Apr',
      'May'      : 'May',
      'June'     : 'Jun',
      'July'     : 'Jul',
      'August'   : 'Aug',
      'September': 'Sep',
      'October'  : 'Oct',
      'November' : 'Nov',
      'December' : 'Dec'
    }[x]

  @staticmethod
  def joke_ordinal_day_of_month_suffix(day_of_month):
    # this incorrectly maps 11 -> 11st, 12 -> 12nd, 13 -> 13rd
    # kaz: originally i did not notice, but then i thought it was funny
    return {1:"st", 2:"nd", 3:"rd"}.get(int(day_of_month[-1]), "th")

  @staticmethod
  def pattern_scatter(date):
    return pattern_scatter(date, 'WWW MMM DD hh:mm:ss ZZZ YYYY', 'WMDhmsZY')

  @staticmethod
  def fastparse_datetime(date, output_pattern):
    """
    'Tue Feb 04 20:59:49 PST 2023'
    'WWW mmm DD HH:MM:SS ZZZ YYYY'
    """

    # %e is day of month with spaces as left padding instead of a zero, i.e. ' 4' instead of '04'
    # %d uses zero padding, so '04'
    #                              "+%a %b %e %T %Z %Y"
    #                              "+%a %b %e %H:%M:%S %Z %Y"
    if (x := pattern_scatter(date, 'WWW mmm DD HH:MM:SS ZZZ YYYY', 'WmDHMSZY')) != False:
      match output_pattern:
        # used for a concise timestamp on the page
        case '+%T':
          return x['H'] + ':' + x['M'] + ':' + x['S']

        # used to check for new days when rendering sections
        case '+%b %e %Y':
          # %b == mmm  abbreviate locale month
          # %d == DD   day of month
          # %Y == YYYY year
          return x['m'] + ' ' + x['D'] + ' ' + x['Y']

        case '+%e %a %B %Y':
          # %e == DD space padded date
          # %a == WWW
          # %Y == YYYY
          # %B == to_full(mmm) full month name
          return x['D'] + ' ' + x['W'] + ' ' + x['Y'] + ' ' + x['m']

        case '+%T %Z':
          return x['H'] + ':' + x['M'] + ':' + x['S'] + ' ' + x['Z']

    return False
