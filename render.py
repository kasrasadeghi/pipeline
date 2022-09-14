class RENDER:
  @staticmethod
  def base_page(D):
    """
    D is a magic_dict with keys: { title, bar, content }
    bar=None renders the default bar with RENDER_UTIL.nav()

    USAGE:
    - RENDER_UTIL.base_page(DICT(title, bar, content))
    - RENDER_UTIL.base_page(DICT(title, bar, content=result))
    - RENDER_UTIL.base_page(DICT(title, content, bar=None))
    """
    if D.bar is None or D.bar == "":
      bar = "".join(RENDER_UTIL.nav())
    else:
      bar = D.bar

    result = (
      f"<!DOCTYPE hmtl><html><head>{RENDER_UTIL.STYLE()}<title>{D.title}</title></head>"
      f"<body>{bar}<div class=\"content\">"
        f'<h1 class="title">{D.title}</h1>'
        f"{D.content}"
      f"</div></body></html>"
    )
    return Response(result, mimetype="text/html")
