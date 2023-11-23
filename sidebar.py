class SIDEBAR:
  @staticmethod
  def render():
    view, note = FLASK_UTIL.CURRENT_NOTE()
    forward_link_list = []
    if note.endswith('.note') and view == 'disc':
      forward_link_list = GRAPH.collect_refs(note)

    def render_forward(note):
      return f'<li class="link-button"><a style="margin-top: 20px" href="{FLAT.to_url(note, view="disc")}">{FLAT.title(note)}</a></li>'

    toggler_name = "sidebar-toggler"
    label_name = toggler_name + "_label"

    return f"""
      <style>

      input#{toggler_name}:checked ~ aside {{
        transition: all var(--sidebar_animation_time) ease-in 0s;
        transform: translateX(-100%);
      }}

      aside {{
        top: var(--navbar_size);
        position: fixed;
        z-index: 15;
        width: 100%;
        height: -webkit-fill-available;
        background-color: #000a;
        transition: all var(--sidebar_animation_time) ease-in 0s;
      }}
      </style>
      <label id="{label_name}" class="nav-button unselectable" for="{toggler_name}">&lt;menu</label>
      <input type="checkbox" id="{toggler_name}" checked style='display: none'/>
      <aside>
        <div class="sidebar-content">
          {RENDER_UTIL.textform(action='/search', name='Search', method='GET')}
          <div class='sidebar-buttons'>
            {RENDER_UTIL.button('yesterday')}
            {RENDER_UTIL.button('recents')}
            {RENDER_UTIL.jsbutton(onclick='toggle_time()', ident='toggle_time', label='toggle time')}
            {RENDER_UTIL.jsbutton(onclick='tvbrightnessup()', ident='tvbrightnessup', label='tv brightness up')}
            {RENDER_UTIL.jsbutton(onclick='tvbrightnessdown()', ident='tvbrightnessdown', label='tv brightness down')}
            <a class="link-button" href='javascript:void(0)'>
              <input onclick="store_preventing()" type="checkbox" id="prevent-default" name="prevent-default" value="Boat">
              <label for="prevent-default">offline</label>
            </a>
          </div>
          <br/>
          <p id='updated-at'> error getting geolocation data </p>
          <button onclick="getLocation()">refresh</button>
          <ul>""" + "<br/>".join(map(render_forward, forward_link_list)) + """</ul>
        </div>
      </aside>
    """
