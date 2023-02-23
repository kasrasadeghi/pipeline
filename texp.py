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
        raise StopIteration(f"couldn't find '{i}' in {self}")
    return self.children[i]

  def get(self):
    return self.children[0]

  def at(self, i):
    assert len(self[i]) == 1
    return self[i].get()

  def push(self, o):
    assert Texp.typecheck(o), f"child '{o}' in Texp.push is neither Texp nor str"
    return self.children.append(o)

  def __len__(self):
    return len(self.children)

  def __iter__(self):
    return iter(self.children)

  def __eq__(self, o):
    if isinstance(o, str):
      o = Texp.parse(o)
    return self.value == o.value and self.children == o.children

  @staticmethod
  def parse(S):
    done = lambda: len(S) == 0
    peek = lambda: S[0]
    more = lambda: len(S) > 0
    def expect(c):
      assert c == peek()
      chomp()
    def chomp():
      nonlocal S
      x, S = S[0], S[1:]
      return x
    def gulp(kind, check):
      acc = ''
      prev = None
      # print('-', S)
      while check(prev):
        if not more():
          raise Exception(f"ERROR, no more to parse while gulping '{kind}'")
        # print('=', S)
        prev = peek()
        acc += chomp()
      return acc

    pWord = lambda: gulp('word', lambda _: peek() not in '() \t\n\r')
    pStr  = lambda: gulp('str', lambda prev: not (S.startswith('"') and prev != '\\'))
    pChar = lambda: gulp('char', lambda prev: not (S.startswith('\'') and prev != '\\'))
    pInt  = lambda: gulp('int', lambda _: peek() not in '() \t\n\r')
    def pAtom():
      match peek():
        case "'":
          expect("'")
          char = pChar()
          expect("'")
          return char
        case '"':
          expect('"')
          str = pStr()
          expect('"')
          return str
      word = pWord()
      if all(c in '0123456879' for c in word):
        return int(word)
      else:
        return word
    def cWS():
      return gulp('whitespace', lambda _: peek() in ' \t\n\r')
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

  def dump(T):
    return T.format()

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
      return len(S) > 2 and S[0] == '{' and S[-1] == '}'

    def submatch(A, B):
      match (A, B):
        case (Texp(), Texp()):
          return A.match_(B, acc)
        case (int(), int()):
          return A == B, acc
        case (int(), str()):
          if is_capture(B):
            key = B[1:-1]
            acc.push(Texp(key, A))
            return True, acc
          return False, acc
        case (str(), str()):
          if is_capture(B):
            key = B[1:-1]
            acc.push(Texp(key, A))
            return True, acc
          return A == B, acc
      raise Exception('unhandled case')

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
