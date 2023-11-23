# a context and hook management system, using kwargs-style hooks like RENDER below
class CONTEXT:
  @staticmethod
  def DEFAULT(kwargs, key):
    """ return a copy with the given key removed """
    default = dict(kwargs)
    if key in default:
      del default[key]
    return default

# the tree renderer, with hooks
class RENDER:
  @staticmethod
  def textblock(x):
    return f'<div style="background: #224; margin: 3px; padding: 6px; border-radius: 10px; font-size: 14px; font-family: Arial, sans-serif; overflow-x: auto" class="kscroll">{x}</div>'

  @staticmethod
  def simple_link(url, **kwargs):
    return f'<a href="{url}">{url}</a>'

  #staticmethod
  def ref(url, **kwargs):
    # [/disc/]<note uuid>#<timestamp fragment>
    from urllib.parse import unquote_plus
    note = url.path.removeprefix('/disc/')
    title = FLAT.title(note)

    if not url.fragment:
      return f"<a href='/disc/{note}'>{title}</a>"

    timestamp_id = unquote_plus(url.fragment)

    # possibilities:
    #
    # same note, journal
    # - @ 10:07:33
    # - @ 10:07:33 on Mar 26       # ref on different day than journal title
    # - @ 10:07:33 on Mar 26 2023  # ref on different day and year than journal title
    # same note, not journal
    # - @ 10:07:33 on Mar 26 2023
    # - should we use the different day journal conciseness, maybe using creation date?
    # not same note, ref journal
    # - Mar 26 2023 @ 10:07:33
    # not same note, ref not journal
    # - whatever @ 10:07:33 on Mar 26 2023

    # same note
    x = DATE.pattern_scatter(timestamp_id)
    if not x:
      return f"<a href='/disc/{note}'>{title}</a>"
    hms = f"{x['h']}:{x['m']}:{x['s']}"
    MDY = f"{x['M']} {x['D']} {x['Y']}"
    if note == kwargs['origin_note']:
      # journal
      if JOURNAL.is_journal(note):
        full_month, ordinal_day, year = title.split(' ')
        title = ''
        day = (ordinal_day
               .removesuffix(',')
               .removesuffix('st')
               .removesuffix('nd')
               .removesuffix('rd')
               .removesuffix('th'))  # 1st, 2nd, 3rd, 4th
        month = DATE.full_month_to_abbr(full_month)
        if x['M'] == month and x['D'] == day and x['Y'] == year:
          # NOTE: timezone changes because of daylight savings and stuff might mess this up
          timestamp = hms
        elif x['Y'] == year:
          timestamp = f"{hms} on {x['M']} {x['D']}"
        else:
          timestamp = f"{hms} on {MDY}"

      # not journal
      else:
        title = ''
        timestamp = f"{hms} on {MDY}"

    # not same note
    else:
      if JOURNAL.is_journal(note):
        title     = MDY
        timestamp = hms
      else:
        timestamp = timestamp_id
        pass

    target_msg = QUOTE.message(note, timestamp_id)
    if target_msg:
      quote = target_msg['content'].removeprefix('msg: ')
    else:
      quote = 'unknown'
    # assert False

    if quote:
      return f"<a class='quote-box' href='/disc/{note}#{url.fragment}'>{title} @ {timestamp}: <span class='quote-msg'>{quote}</span></a>"

    if title:
      return f"<a href='/disc/{note}#{url.fragment}'>{title} @ {timestamp}</a>"

    return f"<a href='/disc/{note}#{url.fragment}'>@ {timestamp}</a>"


  @staticmethod
  def internal_link(url, **kwargs):
    if FLAT.exists(url.path.removeprefix('/disc/')):
      return RENDER.ref(url, **kwargs)

    return RENDER.simple_link(url.path)

  @staticmethod
  def note(note, **kwargs):
    if 'render_note' in kwargs:
      return kwargs['render_note'](note, **kwargs)
    return f'<a href="{FLAT.to_url(note, view="disc")}">{note}</a>'

  @staticmethod
  def link(line, **kwargs):
    match line:
      case {'link': x, 'linktype': 'simple-link'}:
        return RENDER.simple_link(x, **kwargs)
      case {'link': x, 'linktype': 'note'}:
        return RENDER.note(x, **kwargs)
      case {'link': x, 'linktype': 'root-link'}:
        return RENDER.simple_link(x, **kwargs)
      case {'link': x, 'linktype': 'internal-link'}:
        return RENDER.internal_link(x, **kwargs)
      case _:
        raise NotImplementedError(line)

  @staticmethod
  def line_content(content, **kwargs):
    match content:
      case {'tag': tag}:
        return '<emph class="tag">' + tag + '</emph>'
      case {'cmd': cmd}:
        return '<emph class="cmd">' + cmd + '</emph>'
      case str():
        return content
      case {'link': _, 'linktype': _} as link:
        return ': ' + RENDER.link(link, **kwargs)
      case _:
        raise NotImplementedError(content)

  @staticmethod
  def line(line, **kwargs):
    def mapper(x):
      return RENDER.line_content(x, **kwargs)
    return ''.join(map(mapper, line))

  @staticmethod
  def indent(node):
    level = node['indent']
    if level == -1:  # toplevel
      return  ""
    elif level == 0:
      return  "- "
    else:
      return (level * "  ") + "- "

  @staticmethod
  def node(item, **kwargs):
    LOG({'item': item})

    indent = RENDER.indent(item)

    acc = ["<pre>" + indent + RENDER.line(item['line'], indent=indent, **kwargs) + "</pre>"]
    for child in item['children']:
      acc.append(RENDER.node(child, **kwargs))

    return "".join(acc)

  @staticmethod
  def block(block, **kwargs):
    match block:
      case {'msg': _} as msg:
        def default_render_msg(msg):
          return DISCUSSION_RENDER.msg(msg, **kwargs)
        return kwargs.get('render_msg', default_render_msg)(msg)
      case {'line': line}:
        return RENDER.line(line, **kwargs)
    if block == []:
      return '<br/>'

    acc = []
    for item in block:
      match item:
        case {'value': _, 'indent': _, 'children': _, 'line': _}:
          acc.append(RENDER.node(item, **kwargs))
        case {'line': line}:
          rendered_line = RENDER.line(line, **kwargs)
          if len(rendered_line) < 100:
            rendered_line = '<pre>' + rendered_line + '</pre>'
          else:
            rendered_line = '<p style="margin:0">' + rendered_line + '</p>'
          acc.append(rendered_line)
        case _:
          assert False, f"'{item}' is not item in block"

    return '\n'.join(acc)

  @staticmethod
  def root(root, **kwargs):
    match root:
      case {'root': 'pre_roots', 'children': children}:
        return ''.join(map(lambda x: RENDER.block(x, **kwargs), children))
      case {'root': _, 'children': [child]}:
        return RENDER.block(child, **kwargs)
      case {'root': 'nonfinal', 'children': children}:
        details = "<details>"
      case {'root': 'final', 'children': children}:
        details = "<details open>"

    tags = list()
    for item in children[1:]:
      match item:
        case {'msg': [*line_parts]}:
          for lp in line_parts:
            match lp:
              case {'tag': _}:
                tags.append(lp)

    acc = list()
    scrollblock = None
    for i, item in enumerate(children):
      match item:
        case {'msg': _} as msg:
          if scrollblock:
            acc.append(RENDER.textblock(''.join(scrollblock)))
            scrollblock = None

          if i == 0:
            acc.append('<summary>')
            acc.append(DISCUSSION_RENDER.msg(item, **kwargs))
            if tags:
              acc.append("<div class='tags-summary'>" + ' '.join(map(RENDER.line_content,tags)) + "</div>")
            acc.append('</summary>')
          else:
            assert msg['content'].startswith('msg: - '), 'non-roots should start with a dash ("- ")'
            acc.append(DISCUSSION_RENDER.msg(msg, **kwargs))
        case _:
          if scrollblock == None:
            scrollblock = []
          scrollblock.append(RENDER.block(item, **kwargs))

    if scrollblock:
      acc.append(RENDER.textblock(''.join(scrollblock)))

    return details + ''.join(acc) + '</details>'

  @staticmethod
  def section(section, **kwargs):
    # LOG({'kwargs': kwargs, 'section': section['title']})
    if 'render_section' in kwargs:
      return kwargs['render_section'](section, **kwargs)

    if section['title'] == 'HTML':
      LOG({'html section': section})
      acc = []
      for l in section['lines']:
        acc.append(l)
      return "\n".join(acc)

    if section['title'] == 'METADATA':
      if JOURNAL.is_journal_from_section(section):
        return JOURNAL_RENDER.METADATA(FLAT.parse_metadata_from_section(section), **kwargs)
      return '<pre>' + "\n".join(section['lines']) + '</pre>'

    acc = list()
    if section['title'] != 'entry':
      acc.append(f"<pre>--- {section['title']} --- </pre>")

    if 'roots' in section:
      for root in section['roots']:
        acc.append(RENDER.root(root, **kwargs))
    else:
      for block in section['blocks']:
        acc.append(RENDER.block(block, **kwargs))

    return '\n'.join(acc)

  @staticmethod
  def page(note, sections, **kwargs):
    kwargs['origin_note'] = note
    return '\n'.join(map(lambda x: RENDER.section(x, **kwargs), sections)) + TREE.filesize(note)

  @staticmethod
  def content(note, **kwargs):
    return RENDER.page(note, REWRITE.note(note), **kwargs)

  @staticmethod
  def base_page(D):
    """ D is a dict with keys: { title, bar, content } """
    if 'bar' not in D or D['bar'] is None or D['bar'] == "":
      bar = RENDER_UTIL.nav()
    else:
      bar = D['bar']
    footer = D.get('footer', '')
    if footer:
      footer = f"<footer>{footer}</footer>"

    title = D.get('title')
    if D.get('title-render', True):
      title = f"<h1 class='title'>{D['title']}</h1>"
    else:
      title = ''

    result = (
      f"<!DOCTYPE hmtl>"
      + f"<html><head>"
        f"<title>{D['title']}</title>"
        + RENDER_UTIL.STYLE()
        # + FLASK_UTIL.TELEMETRY()
        + include_js('toggle_time.js')
        + include_js('highlight_selected.js')
        + include_js('disc.js')
        + include_js('tv_brightness.js')
      + "</head>"
      f"<body onload='init_time_display()'>"
        f"{bar}"
        f"<main id='main'>"
          f"{title}"
          f"{D['content']}"
        "</main>"
        f"{footer}"
      f"</body></html>"
    )
    return Response(result, mimetype="text/html")
