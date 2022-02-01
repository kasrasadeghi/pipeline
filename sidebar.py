class SIDEBAR:
  @classmethod
  def render(cls):
    return """
      <aside>
        <div class="sidebar-content">
          <form action="/" method="POST">
            <input class="msg_input" type="text" name="title">
            <input class="link-button" type="submit" value="New Note"/>
          </form>
          <a class="link-button" href="/yesterday">yesterday</a>
          <a class="link-button" href="/recents">recents</a>
        </div>
      </aside>
    """

  @classmethod
  def render_routine():
    """parse the routine file in order to render common things in my daily routine"""
    content = parse_file(FLAT.to_path(routine()))


  @classmethod
  def routine():
    return "7e3e5fea-300a-4a97-ab10-ee6c687f647f.note"
