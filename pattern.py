def pattern_scatter(text, pattern, keys):
  """
  motivational example:
  text:    'Tue Feb 04 20:59:49 PST 2023'
  pattern: 'WWW mmm DD HH:MM:SS ZZZ YYYY'
  keys:    'WmDHMSZY'
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
