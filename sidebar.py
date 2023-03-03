class SIDEBAR:
  @classmethod
  def render(cls):
    view, note = FLASK_UTIL.CURRENT_NOTE()
    forward_link_list = []
    if note.endswith('.note') and view == 'disc':
      forward_link_list = GRAPH.collect_refs(note)

    def render_forward(note):
      return f'<li class="link-button"><a style="margin-top: 20px" href="{FLAT.to_url(note, view="disc")}">{FLAT.title(note)}</a></li>'

    return f"""
      <aside>
        <div class="sidebar-content">
          {RENDER_UTIL.button(action='/', name='New Note')}
          {RENDER_UTIL.button(action='/search', name='Search', method='GET')}
          <a class="link-button" href="/yesterday">yesterday</a>
          <a class="link-button" href="/recents">recents</a>
          <a class="link-button" href='javascript:void(0)'>
            <input onclick="store_preventing()" type="checkbox" id="prevent-default" name="prevent-default" value="Boat">
            <label for="prevent-default">offline</label>
          </a>
          <br/>
          <p id='updated-at'> error getting geolocation data </p>
          <button onclick="getLocation()">refresh</button>
          <ul>""" + "<br/>".join(map(render_forward, forward_link_list)) + """</ul>
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
