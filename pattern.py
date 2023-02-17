def pattern_scatter(text, pattern, keys):
  """
  motivational example:
  'Tue Feb 04 20:59:49 PST 2023'
  'WWW mmm DD HH:MM:SS ZZZ YYYY'
  'WmDHMSZY'
  """

  if len(text) != len(pattern):
    return False

  from collections import defaultdict
  result = defaultdict(lambda: '')
  for a, match in zip(text, pattern):
    if match in keys:
      result[match] += a
    else:
      if a != match:
        return False

  return result

def fastparse_datetime(date, output_pattern):
  """
  'Tue Feb 04 20:59:49 PST 2023'
  'WWW mmm DD HH:MM:SS ZZZ YYYY'
  """

  abbr_month_to_full = {
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
  }

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

  return False
