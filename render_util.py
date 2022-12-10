class RENDER_UTIL:
  @classmethod
  def STYLE(_):
    # old font size: clamp(2vmin, 1rem + 2vw, 24px);
    # .msg_content: overflow: hidden; text-overflow: ellipsis;
    # .msg: overflow: hidden; max-width: 100%;
    pixels_of_navbar_size = 40 # in pixels
    navbar_size = str(pixels_of_navbar_size) + "px"
    header_color = "#bb6"
    link_button_color = {'main': "orange", 'hover': "red"}
    msg_color = "#a52a2a"
    nav_button_color = "#611"
    base_text_color = "#ddd"
    input_background_color = "#333"
    body_background_color= "#222"
    banner_color = "#aaa"
    sidebar_animation_time = "0.1s"

    meta_tags = ", ".join([
      'height=device-height',
      'width=device-width',
      'initial-scale=1.0',
      'minimum-scale=1.0',
      'maximum-scale=1.0',
      'user-scalable=no',
      'target-densitydpi=device-dpi'
    ])

    return """
     <meta name="viewport" content=" """ + meta_tags + """ ">
     <style>
       body { margin: 0; background: """ + body_background_color + """; }
       .content { padding: 5px; margin: """ + navbar_size + """ 1% 1% 1%; height: calc(100vh - """ + navbar_size + """ - 10px); }
       :target { scroll-margin-top: """ + navbar_size + """; }
       .msgbox { margin: 0px;
             display: flex; flex-direction: column;
             align-content: stretch; align-items: flex-start; }
       pre { margin: 0px; color: """ + base_text_color + """; }
       .msg { display: flex; margin: 3px; font-family: monospace; }
       .msg_timestamp { border-radius: 18px; color: rgb(230, 50, 120); }
       .msg_content {
         display: inline-block;
         padding: 7px 12px 8px 12px;
         border-radius: 18px;
         background: """ + msg_color + """; color: rgb(250, 250, 250);
         overflow-wrap: anywhere;
       }

       .msg_container {
         display: flex;
         flex-direction: row;
         align-items: center;
       }
       .msg_dash {
         margin: 0 0.5em 0 0.5em;
       }

       * { font-size: 18px; color: """ + base_text_color + """; }
       header {
         display: flex; align-items: center;
         position: fixed; top: 0px; width: 100%; height: """ + navbar_size + """;
         background: """ + header_color + """; z-index: 12;
         margin: 0px;
         box-shadow: 0px 0px 11px 2px """ + header_color + """;
       }
       header > a, label#toggle-sidebar-menu {
         margin: 5px;
         padding: 0px 5px;
         color: """ + nav_button_color + """;
       }

       h1.title {
         margin-left: 1em; padding-left: 10px; padding-bottom: 6px; padding-right: 10px;
         border-left: 2px white solid; border-bottom: 2px white solid;
       }

       span.mono {
         font-feature-settings: "liga" 0;
         font-family: monospace;
       }

       details > summary {
         display: block;
       }
       details > summary > div > div > .msg_content {
         border-right: solid 10px #ffa0ab;
       }
       details[open] > summary > div > div > .msg_content {
         border-right: solid 10px #a0abff;
       }
       details > summary > .tags-summary {
         display: true;
       }
       details[open] > summary > .tags-summary {
         display: none;
       }

       .banner-box {
         display: flex;
         flex-direction: row;
         align-items: center;
         width: -webkit-fill-available;
         margin-top: 15px;
       }
       .banner {
         border: solid """ + banner_color + """;
         padding: 3px 7px 3px 5px;
         min-width: fit-content;
       }
       .banner-bar {
         width: -webkit-fill-available;
         height: 3px;
         background: """ + banner_color + """;
       }
       .banner-bar-left {
         height: 3px;
         min-width: 30px;
         background: """ + banner_color + """;
       }

       .editor_textarea {
         background: """ + input_background_color + """;
         height: calc(85vh);
         line-height: 23px;
         resize:none;
         overflow: auto;
         width: -webkit-fill-available;
       }

       .link-button {
         background: none;
         color: """ + link_button_color['main'] + """;
         cursor: pointer;
         font-family: monospace;
         border: """ + link_button_color['main'] + """ 1px solid;
         margin: 2px;
         padding: 6px 6px 4px 6px;
       }
       .link-button:hover, .link-button:focus { border-color: """ + link_button_color['hover'] + """; outline: none; }
       .link-button:active { color: """ + link_button_color['hover'] + """; }

       .msg_input { background: """ + input_background_color + """;width: -webkit-fill-available; margin: 5px}

       /* sidebar */

       .unselectable {
         -webkit-touch-callout: none;
         -webkit-user-select: none;
         -khtml-user-select: none;
         -moz-user-select: none;
         -ms-user-select: none;
         user-select: none;
       }

       input#toggler {
         visibility: hidden;
       }

       input#toggler:checked ~ aside {
         transition: all """ + sidebar_animation_time + """ ease-in 0s;
         transform: translateX(-100%);
       }

       aside {
         top: 40px;
         position: fixed;
         z-index: 15;
         width: 100%;
         height: -webkit-fill-available;
         background-color: #000a;
         transition: all """ + sidebar_animation_time + """ ease-in 0s;
       }

       div.sidebar-content {
         margin: 5%;
       }

       /* end sidebar */

       /* phones */
       @media (max-aspect-ratio: 5/4) {
         .msg { flex-direction: column; align-items: flex-start; }
         .msg_timestamp { margin: 0px 0px 0px 13px; padding: 5px 0px 1px 0px; }
       }

       /* desktop */
       @media (min-aspect-ratio: 5/4) {
         .msg { flex-direction: row; align-items: baseline; }
         .msg_timestamp { margin: 0px 5px 0px 0px; }
       }
     </style>""" + FLASK_UTIL.TELEMETRY()

  @staticmethod
  def kscroll(**kwargs):
    foreground = kwargs.get('foreground', "#777")
    background = kwargs.get('background', "#333")
    size = kwargs.get('size', "10px");
    return """
       .kscroll {
         /* Foreground, Background */
         scrollbar-color: """ + (foreground + " " + background) + """;
       }
       .kscroll::-webkit-scrollbar {
         width: """ + size + """; /* Mostly for vertical scrollbars */
         height: """ + size + """; /* Mostly for horizontal scrollbars */
       }
       .kscroll::-webkit-scrollbar-thumb {
         background: """ + foreground + """;
       }
       .kscroll::-webkit-scrollbar-track {
         background: """ + background + """;
       }
    """

  @classmethod
  def ANSI(R):
    return '\x1B['

  @classmethod
  def _parse_color(R, s):
    original = s

    acc = list()

    # chomp until the needle in the haystack
    def chomp(needle):
      before, after = s.split(needle, 1)
      acc.append(before)
      return after

    D = {'31m': '<span style="color:red">',
         'm': '</span>',
         '1m': '<span style="font-weight: bold">',
         '36m': '<span style="color:blue">',
         '1;36m': '<span style="font-weight:bold; color:#00b9f9">',
         '1;32m': '<span style="font-weight:bold; color:green">',
         '1;31m': '<span style="font-weight:bold; color:red">',
         '33m': '<span style="color:orange">',
         '32m': '<span style="color:green">',
         '7;31m': '<span style="background-color:red">',
         }

    ANSI = R.ANSI()
    while True:
      if -1 == s.find(ANSI):
        break

      s = chomp(ANSI)
      for code, replacement in D.items():
        if s.startswith(code):
          acc.append(replacement)
          s = s[len(code):]
          break
      else:
        LOG(f"ERROR: did not find replacement for ANSI code '{s[:5]}'")
        return original

    acc.append(s)

    return "".join(acc)

  # TODO CONSIDER making an "uncolored" function, that takes away the ascii
  #               codes OR the coloring spans from a string

  @classmethod
  def bar(cls):
    return "<div style='width: 90%; background-color: white; height: 2px; margin: 10px'></div>"

  # TODO render a prefix of index inside of the sidebar, using block renderer

  @classmethod
  def button(cls, **kwargs):
    action  = kwargs['action']
    name    = kwargs['name']
    method  = kwargs.get('method', "POST")  # second argument is default
    return f"""
           <form action="{action}" method="{method}">
             <input class="msg_input" type="text" name="content">
             <input class="link-button" type="submit" value="{name}"/>
           </form>
           """

  @classmethod
  def nav(R, *extras) -> list:
    navbar = list()
    navbar.append(f'<header>'
                  f'<input type="checkbox" id="toggler" checked style=""/>'
                  + SIDEBAR.render() +
                  f'<label id="toggle-sidebar-menu" class="unselectable" for="toggler">&lt;menu</label>'
                  f'<a style="" href="/">root</a>'
                  f'<a href="/today">journal</a>'
                  f'<a href="/git/menu">git</a>')

    for extra in extras:
      navbar.append(extra)

    navbar.append(f'</header>')
    return "".join(navbar)

  @staticmethod
  def banner(title):
    return ('<div class="banner-box">' +
              "<div class='banner-bar-left'></div>" +
              "<span class='banner'>" + title + "</span>" +
              "<div class='banner-bar'></div>" +
            "</div>")
