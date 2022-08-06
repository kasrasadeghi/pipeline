class BLOG:
  root = "37a95556-2ec0-4f0d-b6af-d3dd263d4763.note"

  @staticmethod
  def parse():
    with FLAT.open_note(BLOG.root) as N:
      # for some reason, "f.readlines()" and "for L in f:" don't usually do what
      # i expect so i'm using splitlines().  I think splitlines handles weird
      # cases with empty last lines and empty front matter correctly, actually
      # preserving them instead of randomly chopping them off
      lines = N.read().splitlines()

    line_iter = iter(enumerate(lines))
    acc = []
    line_i = 0
    def get():
      nonlocal line_i
      line_i, line = next(line_iter)
      return line

    def abort(line):
      return f"ERROR: on line '{i}' '{line}'"

    first_line = get()
    if not first_line.startswith("# "):
      return abort(first_line)

    title = first_line.removeprefix("# ")

    for i, l in line_iter:
      if l == "--- METADATA ---":
        break
      acc.append(l)
    return title, "\n".join(acc)



@app.route("/blog")
def get_blog():
  title, content = BLOG.parse()
  return DEBUG.TEXT(title, content)
