class DATECALC:
  @staticmethod
  def daycount(d):
    if d['m'] == 2:
      # a year has a leap day if:
      # it is a multiple of 4, except if:
      # it is a multiple of 100,
      # except for multiples of 400
      # mul4 and ((not mul100) or mul400)
      # the or makes %400 override %100 when it is true
      # this is not true before 1750, 1700 and below are just every 4 years
      if d['y'] % 4 == 0:
        if d['y'] <= 1700:
          return 29
        else:
          if d['y'] % 100 != 0 or d['y'] % 400 == 0:
            return 29
          else:
            return 28
      else:
        return 28
    elif d['m'] in [1,3,5,7,8,10,12]:
      return 31
    else:
      assert d['m'] in [4,6,9,11]
      return 30

  @staticmethod
  def date_tuple(d):
    return d['y'], d['m'], d['d']

  # a, b of type {'m', 'd', 'y' : int}
  @staticmethod
  def date_before(a, b):
    return date_tuple(a) < date_tuple(b)

  # needed to convert to a datecalc-style dict
  @staticmethod
  def date_to_nums(d):
    d['m'] = ['January', 'February', 'March', 'April',
              'May', 'June', 'July', 'August',
              'September', 'October', 'November', 'December']\
             .index(d['m'])
    d['d'] = int(d['d'].rstrip('stndrdth')) # remove letters from 1st, 2nd, 3rd, 4th
    d['y'] = int(d['y'])
    return d

@app.route('/test/daycount')
def test_daycount():
  import subprocess
  r = []
  yield '<pre>'
  for y in range(1,4000):
    calput = subprocess.check_output("cal feb " + str(y), shell=True)
    dc = DATECALC.daycount({'m':2,'d':1,'y':y})
    adc = 29 if b"29" in calput.split(b"\n", 1)[1] else 28
    if dc != adc:
      yield "<span style='color:red'>"
    tup = (y, dc, adc, dc == adc)
    yield FLASK_UTIL.ESCAPE(json.dumps(tup)) + '\n'
    if dc != adc:
      yield calput.decode('utf8')
      yield "</span>"
  return '</pre>'
