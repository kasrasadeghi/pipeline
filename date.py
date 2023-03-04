class DATE:
  @staticmethod
  def get_timestamp():
    return util.date_cmd("+%a %b %e %T %Z %Y")  # from emacs/lisp/kaz.el's kaz/current-time
"+%a %b %e %T %Z %Y"


# a set of functions that help avoid using util.date_cmd, which relies on a subprocess and thus is slow

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

def joke_ordinal_day_of_month_suffix(day_of_month):
  # this incorrectly maps 11 -> 11st, 12 -> 12nd, 13 -> 13rd
  return {1:"st", 2:"nd", 3:"rd"}.get(int(day_of_month[-1]), "th")

def fastparse_datetime(date, output_pattern=None):
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
