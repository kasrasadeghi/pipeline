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
  currline = firstline[firstline.find("DICT"):]
  lines.append(currline)

  while True:

    # should actually try matching parenthesis, not this underapproximation
    if ')' in currline:
      break

    currline = linecache.getline(filename, lineno).strip()
    lines.append(currline)

    lineno += 1

  # get the argument names from the call site
  argnames = [x.strip() for x in " ".join(lines).removeprefix("DICT(").removesuffix(")").split(",")]
  up = list(zip(argnames, l))
  kwargs.update(up)
  return SimpleNamespace(**kwargs)
