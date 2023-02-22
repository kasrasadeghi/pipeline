class Texp:
  def __init__(self, value, *children):
    self.value = value
    for child in children:
      assert isinstance(child, Texp) or isinstance(child, str), f"child '{child}' in Texp constructor is neither Texp nor str"
    self.children = list(children)

  def __getitem__(self, i):
    return self.children[i]

  def __len__(self):
    return len(self.children)

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
    if not isinstance(T, Texp) and not isinstance(T, str):
      raise Exception(f"'{T}' is not a Texp nor str")
    if isinstance(T, str):
      return repr(T)
    if T.value in toplevels:
      result = '\n(' + T.value + ' ' + ' '.join(map(lambda x: Texp.format(x, *toplevels), T.children))
      if any(map(lambda x: x.value in toplevels, T.children)):
        result += "\n) #" + T.value
      else:
        result += ")"
      return result
    elif T.children:
      return '(' + T.value + ' ' + ' '.join(map(lambda x: Texp.format(x, *toplevels), T.children)) + ')'
    else:
      return T.value

  def dump(T):
    return T.format()

  def __repr__(T):
    return T.dump()
