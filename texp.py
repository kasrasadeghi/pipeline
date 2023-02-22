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

  @staticmethod
  def parse(S):
    done = lambda: len(S) == 0
    peek = lambda: S[0]
    def expect(c):
      assert c == peek()
      chomp()
    def chomp():
      nonlocal S
      x, S = S[0], S[1:]
      return x
    def gulp(check):
      acc = ''
      while check(): acc += chomp()
      return acc

    pWord = lambda: gulp(lambda: peek() not in '() \t\n\r')
    pAtom = lambda: pWord()
    cWS = lambda: gulp(lambda: peek() in ' \t\n\r')
    pTexp = lambda: pList() if peek() == '(' else pAtom()
    def pList():
      expect('(')
      root = pWord()
      cWS()
      children = []
      while peek() != ')':
        children.append(pTexp())
        cWS()
      expect(')')
      return Texp(root, children)

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
