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
