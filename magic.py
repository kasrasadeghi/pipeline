from types import SimpleNamespace
import linecache  # getline
import inspect  # currentframe

# make a namespace
# but take the arguments in l and put them in kwargs with whatever their callsite name is
def DICT(*l, **kwargs):
  if 0 == len(l):
    return SimpleNamespace(**kwargs)

  caller_frame = inspect.currentframe().f_back
  caller_code, lineno = caller_frame.f_code, caller_frame.f_lineno
  filename = caller_code.co_filename
  firstline = linecache.getline(filename, lineno).strip()

  lines = list()
  done = False
  # parse until the first close-paren
  def consider_append(line):
    nonlocal lines
    nonlocal done
    if ')' in line:
      line = line[:line.find(')')]
      done = True
    lines.append(line)

  currline = firstline[firstline.find("DICT"):]
  consider_append(currline)

  while not done:
    # should actually try matching parenthesis, not this underapproximation
    consider_append(currline)

    currline = linecache.getline(filename, lineno).strip()
    lineno += 1

  # get the argument names from the call site
  args = " ".join(lines).removeprefix("DICT(").removesuffix(")").split(",")
  non_kwargs = filter(lambda y: '=' not in y, args)  # ignore args with '=' in them
  argnames = [x.strip() for x in non_kwargs]
  up = list(zip(argnames, l))
  kwargs.update(up)
  return SimpleNamespace(**kwargs)
