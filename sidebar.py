class SIDEBAR:
  @classmethod
  def render(cls):
    return f"""
      <aside>
        <div class="sidebar-content">
          {RENDER_UTIL.button(action='/', name='New Note')}
          {RENDER_UTIL.button(action='/search', name='Search', method='GET')}
          <a class="link-button" href="/yesterday">yesterday</a>
          <a class="link-button" href="/recents">recents</a>
        </div>
      </aside>
    """

  @classmethod
  def render_routine():
    """parse the routine file in order to render common things in my daily routine"""
    content = parse_file(FLAT.to_path(routine()))
    # TODO

  @classmethod
  def routine():
    return "7e3e5fea-300a-4a97-ab10-ee6c687f647f.note"
