class Texp:
  def __init__(self, value, *children):
    self.value = value
    for i, child in enumerate(children):
      assert Texp.typecheck(child), f"child #{i} '{child}' in Texp constructor is neither Texp nor str"
    self.children = list(children)

  @staticmethod
  def typecheck(o):  # children must be Texp, str, or int
    return isinstance(o, (Texp, str, int))

  def __getitem__(self, i):
    if isinstance(i, str):
      key = i
      try:
        return next(c for c in self.children if c.value == key)
      except StopIteration:
        raise ValueError(f"couldn't find '{i}' in {self}")
    return self.children[i]

  def __contains__(self, key):
    assert isinstance(key, str)
    try:
      next(c for c in self.children if c.value == key)
      return True
    except StopIteration:
      return False

  def get(self, *args):
    if len(args) == 1:     # TODO allow a default value if len(args) == 2
      assert len(self[args[0]]) == 1
      return self[args[0]][0]
    elif len(args) > 1:
      raise ValueError(f"'{self}'.get({args})")
    assert len(self.children) == 1
    return self.children[0]

  def push(self, o):
    assert Texp.typecheck(o), f"child '{o}' in Texp.push is neither Texp nor str"
    return self.children.append(o)

  def __len__(self):
    return len(self.children)

  def __iter__(self):
    return iter(self.children)

  def __eq__(self, o):
    # if isinstance(o, str):   # CONSIDER maybe have string coalescing, hmmm
    #   o = Texp.parse(o)
    if not isinstance(o, Texp):  # no coalescing, for now...
      return False
    return self.value == o.value and self.children == o.children

  @staticmethod
  def parse(S):
    done = lambda: len(S) == 0
    peek = lambda: S[0]
    more = lambda: len(S) > 0
    def expect(c):
      assert more()
      assert c == peek()
      return chomp()
    def chomp():
      nonlocal S
      x, S = S[0], S[1:]
      return x

    def gulp(kind, check):
      acc = ''
      prev = None
      # print(kind + '-', S)
      while check(prev):
        if not more():
          raise Exception(f"ERROR, no more to parse while gulping '{kind}'")
        # print(kind + '=', S)
        prev = peek()
        acc += chomp()
        assert more(), f"should be more while parsing '{kind}'"
      return acc
    cWS   = lambda: gulp('whitespace', lambda _: peek() in ' \t\n\r')
    pWord = lambda: gulp('word', lambda _: peek() not in '() \t\n\r')
    pStr  = lambda: gulp('str', lambda prev: not (S.startswith('"') and prev != '\\'))
    pChar = lambda: gulp('char', lambda prev: not (S.startswith('\'') and prev != '\\'))
    pInt  = lambda: gulp('int', lambda _: peek() not in '() \t\n\r')

    def pAtom():
      match peek():
        case "'":
          return Texp(expect('\'') + pChar() + expect('\''))
        case '"':
          return Texp(expect('"') + pStr() + expect('"'))
      word = pWord()
      if all(c in '0123456879' for c in word):
        return int(word)
      else:
        return Texp(word)
    def pTexp():
      return pList() if peek() == '(' else pAtom()
    def pList():
      expect('(')
      root = pWord()
      cWS()
      children = []
      while peek() != ')':
        children.append(pTexp())
        cWS()
      expect(')')
      return Texp(root, *children)

    return pTexp()

  def format(T, *toplevels):
    if not Texp.typecheck(T):
      raise Exception(f"'{T}' is not a Texp nor str nor int")
    if isinstance(T, (str, int)):
      return repr(T)
    if T.value in toplevels:
      result = '\n(' + T.value
      if T.children:
        result += ' ' + ' '.join(map(lambda x: Texp.format(x, *toplevels), T.children))
      if any(map(lambda x: isinstance(x, Texp) and x.value in toplevels, T.children)):
        result += "\n) #" + T.value
      else:
        result += ")"
      return result
    elif T.children:
      return '(' + T.value + ' ' + ' '.join(map(lambda x: Texp.format(x), T.children)) + ')'
    else:
      return T.value

  @staticmethod
  def dump_(T):
    if isinstance(T, str):
      return 'str=' + repr(T)
    if isinstance(T, int):
      return 'int=' + repr(T)
    if T.children:
      return 'texp=(' + T.value + ' ' + ' '.join(map(lambda x: Texp.dump_(x), T.children)) + ')'
    else:
      return 'texp='+T.value

  def dump(T):
    return Texp.dump_(T)

  def __repr__(T):
    return T.dump()

  def match(T, pattern):
    if isinstance(pattern, str):
      pattern = Texp.parse(pattern)
    elif not isinstance(pattern, Texp):
      raise Exception(f"'{pattern}' is neither Texp nor str")
    # LOG({'pattern': pattern})
    return T.match_(pattern, Texp('match'))

  def match_(T, o, acc):
    def is_capture(S):
      assert isinstance(S, str)
      return len(S) > 2 and S[0] == '{' and S[-1] == '}'

    def submatch(A, B):
      match (A, B):
        case (Texp(), Texp()):
          return A.match_(B, acc)
        case (int(), int()):
          return A == B, acc
        case (int(), Texp()):
          if is_capture(B.value):
            key = B.value[1:-1]
            acc.push(Texp(key, A))
            return True, acc
          return False, acc
        case (str(), Texp()):
          if is_capture(B.value):
            key = B.value[1:-1]
            acc.push(Texp(key, A))
            return True, acc
          return A == B.value, acc
        case (str(), str()):
          if is_capture(B):
            key = B[1:-1]
            acc.push(Texp(key, A))
            return True, acc
          return A == B, acc
      raise Exception(f"unhandled case: '{A}'/{type(A)} '{B}'/{type(B)}")

    if is_capture(o.value):
      # use the value of the pattern as the key in the accumulator
      key = o.value[1:-1]
      acc.push(Texp(key, T.value))
    else:
      if T.value != o.value:
        return False, acc

    # check the children if they're both texps
    if isinstance(T, Texp) and isinstance(o, Texp):
      if len(T) != len(o):
        return False, acc

      for Tc, oc in zip(T.children, o.children):
        if not (x := submatch(Tc, oc))[0]:
          return x

    return True, acc
