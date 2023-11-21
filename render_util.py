BASE_STYLE = """
/* global font setting */
 * { font-size: 18px; color: var(--base_text_color); }

:root {
  --main_padding: 10px;
  --main_height: calc(100dvh - var(--navbar_size) - var(--footer_menu_size) - 2*var(--main_padding));
}

/* initial layout */
body {
  margin: 0;
  background: var(--body_background_color);
}
header {
  display: flex; align-items: center;
  width: 100%;
  position: absolute; top: 0; left: 0;
  height: var(--navbar_size);
  margin: 0px;
  z-index: 12;
}
footer {
  background: #552909;
  width: 100%;
  height: var(--footer_menu_size);
  position: absolute; bottom: 0; left: 0;
  z-index: 12;
}
main {
  position: absolute; top: var(--navbar_size); left: 0;
  height: var(--main_height);
  width: -webkit-fill-available;
  padding: var(--main_padding);
  overflow-y: scroll;
}

/* colored layout */
header {
  box-shadow: 0px 0px 11px 2px var(--header_color);
  background: var(--header_color);
}
header > a, label#toggle-sidebar-menu {
  margin: 5px;
  padding: 0px 5px;
  color: var(--nav_button_color);
}

/* forms */
select, option, input[type=button], input[type=button], button, input[type=text] { color: black }
input[type=text].msg_input { color: var(--base_text_color) }
input[type=checkbox] { width: 18px; height: 18px; margin: 1px 3px 1px 3px; padding: 0 }

/* disc messages */
.msglist {
  margin: 0px;
  display: flex;
  flex-direction: column;
  align-content: stretch;
  align-items: flex-start;
  font-feature-settings: "liga" 0;
}
.msg { display: flex; margin: 3px; font-family: monospace; }
.msg_timestamp { border-radius: 18px; color: var(--msg_timestamp_color); }
.msg_content {
  padding: 7px 12px 8px 12px;
  border-radius: 18px;
  background: var(--msg_color); color: rgb(250, 250, 250);
}
pre { margin: 0px; color: var(--base_text_color); }

/* selecting specific messages */
.selected { width: 100%; background: #0cc4; border-radius: 18px }
.selected > .msg_timestamp { color: #ddd; }

/* tags */
emph.tag { color: var(--tag_color); font-weight: 500; }
emph.cmd { color: var(--cmd_color); }

/* note title */
h1.title {
  margin-left: 1em; padding-left: 10px; padding-bottom: 6px; padding-right: 10px;
  border-left: 2px white solid; border-bottom: 2px white solid;
}

/* debug */
span.mono {
  font-feature-settings: "liga" 0;
  font-family: monospace;
}

/* disc roots */
.msg_container {
  display: flex;
  flex-direction: row;
  align-items: center;
  overflow-wrap: anywhere;
}
.msg_dash {
  margin: 0 0.5em 0 0.5em;
}

/* collapsing roots */
details { width: 100%; }
details > summary {
  display: inline-block;  /* to prevent 'list-item' display type*/
}
details > summary > div > div > .msg_content {
  border-right: solid 10px #ffa0ab;
}
details[open] > summary > div > div > .msg_content {
  border-right: solid 10px #a0abff;
}
/* - only show the tag summary for collapsed tags */
details > summary > .tags-summary {
  display: true;
}
details[open] > summary > .tags-summary {
  display: none;
}

/* quote */
.quote-box { color: var(--quote_timestamp_color); }
.quote-msg { color: white; }

/* banner */
.banner-box {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: -webkit-fill-available;
  margin-top: 15px;
}
.banner {
  border: solid var(--banner_color);
  padding: 3px 7px 3px 5px;
  min-width: fit-content;
}
.banner-bar {
  width: -webkit-fill-available;
  height: 3px;
  background: var(--banner_color);
}
.banner-bar-left {
  height: 3px;
  min-width: 30px;
  background: var(--banner_color);
}

/* edit */
.editor_container {
  display: flex;
  flex-direction: column;
  height: 100%;
  margin: 0px;
}
#editor_submit-button {
  margin-top: 5px;
  width: 100%;
}
.editor_textarea {
  background: var(--input_background_color);
  box-sizing: border-box;
  height: 100%;
  line-height: 23px;
  resize:none;
  overflow: auto;
  width: -webkit-fill-available;
}

/* buttons */
.link-button {
  background: none;
  color: var(--link_button_main_color);
  cursor: pointer;
  font-family: monospace;
  border: var(--link_button_main_color) 1px solid;
  margin: 2px;
  padding: 6px 6px 4px 6px;
}
.link-button:hover, .link-button:focus { border-color: var(--link_button_hover_color); outline: none; }
.link-button:active { color: var(--link_button_hovercolor); }

.sidebar-buttons {
  display:flex;
  width: 100%;
  flex-wrap: wrap;
  flex-direction: row;
}

/* disc input */
#msg_input {
  background: var(--input_background_color);
  margin: 5px;
  width: -webkit-fill-available;
}

.disc-buttons {
  display:flex;
  width: 100%;
  flex-wrap: wrap;
  flex-direction: row;
}

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
  transition: all var(--sidebar_animation_time) ease-in 0s;
  transform: translateX(-100%);
}

aside {
  top: 40px;
  position: fixed;
  z-index: 15;
  width: 100%;
  height: -webkit-fill-available;
  background-color: #000a;
  transition: all var(--sidebar_animation_time) ease-in 0s;
}

div.sidebar-content {
  margin: 5%;
}

/* phones */
@media (max-width: $desktopview_device_width_threshold) {
  .msg { flex-direction: column; align-items: flex-start; }
  .msg_timestamp { margin: 0px 0px 0px 13px; padding: 5px 0px 1px 0px; }
  .editor_textarea { font-size: 14px; line-height: 20px; }
}

/* desktop */
@media (min-width: $desktopview_device_width_threshold) {
  .msg { flex-direction: row; align-items: baseline; }
  .msg_timestamp { margin: 0px 5px 0px 5px; }
}

"""

class RENDER_UTIL:
  @classmethod
  def STYLE(_):
    # old font size: clamp(2vmin, 1rem + 2vw, 24px);
    # .msg_content: overflow: hidden; text-overflow: ellipsis;
    # .msg: overflow: hidden; max-width: 100%;

    C = FLAT.default_config() | FLAT.config()

    # make a css variable like --example for each var in config C
    # used like var(--example) in css
    css_vars = ":root {\n" + "\n".join(f"  --{name}: {value};" for name, value in C.items()) + "\n}"

    # you can't have css vars in media queries
    style = css_vars + BASE_STYLE.replace('$desktopview_device_width_threshold', C['desktopview_device_width_threshold'])

    meta_tags = ", ".join([
      'height=device-height',
      'width=device-width',
      'initial-scale=1.0',
      'minimum-scale=1.0',
      'maximum-scale=1.0',
      'user-scalable=no',
      'target-densitydpi=device-dpi'
    ])

    return (f'<meta name="viewport" content="{meta_tags}">'
            f'<style>{style}\n{RENDER_UTIL.kscroll(foreground="#f88", background="#888")}</style>')

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
  def textform(cls, **kwargs):
    action  = kwargs['action']
    name    = kwargs['name']
    method  = kwargs.get('method', "POST")  # POST is default
    return f"""
           <form action="{action}" method="{method}">
             <input class="text-input" type="text" name="content">
             <input class="link-button" type="submit" value="{name}"/>
           </form>
           """

  @staticmethod
  def jsbutton(**kwargs):
    onclick = kwargs['onclick']
    ident = kwargs['ident']
    label = kwargs['label']
    return f"<a class='link-button' id='{ident}' href='javascript:void(0)' onclick='{onclick}'>{label}</a>"

  @classmethod
  def nav(R, *extras) -> str:
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

  @staticmethod
  def collapse(show, content):
    return f"""<details><summary>{show}</summary>{content}</details>"""

  @staticmethod
  def pre(s):
    return "<pre>" + str(s) + "</pre>"
