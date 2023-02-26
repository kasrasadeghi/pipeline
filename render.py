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
  def link(url, **kwargs):
    if 'view' in kwargs:
      if kwargs['view'] == 'ref':
        ref = REF.parse_ref(url)
        if '#' not in ref:
          LOG({'ref no #': ref})
        else:
          note, timestamp = ref.split('#')
          if 'Tags' in FLAT.metadata(note) and 'Journal' in FLAT.metadata(note)['Tags']:
            return f'<a href="{url}">{FLAT.title(note)} @ {timestamp[17:25]}</a>'
          else:
            from urllib.parse import unquote_plus
            return f'<a href="{url}">{FLAT.title(note)} @ {unquote_plus(timestamp)}</a>'

      LOG({'ERROR: unmatched link view': kwargs['view']})
    return f'<a href="{url}">{url}</a>'

  @staticmethod
  def note(note, **kwargs):
    # LOG({'kwargs': kwargs})
    if 'render_note' in kwargs:
      return kwargs['render_note'](note, **kwargs)
    return f'<a href="{FLAT.to_url(note, view="disc")}">{note}</a>'

  @staticmethod
  def tag(s):
    match s:
      case {'tag': tag}:
        return '<emph class="tag">' + tag + '</emph>'
      case {'cmd': cmd}:
        return '<emph class="cmd">' + cmd + '</emph>'
      case str():
        return s
      case _:
        NotImplementedError()

  @staticmethod
  def line_content(content):
    return ''.join(map(RENDER.tag, TAG.parse(content)))

  @staticmethod
  def line(L, **kwargs):
    acc = list()
    for el in L:
      match el:
        case {'link': link}:
          acc.append(RENDER.link(link))
        case {'note': note}:
          acc.append(RENDER.note(note))
        case {'internal-link': internal_link}:
          acc.append(RENDER.link(internal_link))
        case {'url-internal-link': internal_url}:
          acc.append(RENDER.link(internal_url))
        case _:
          acc.append(RENDER.line_content(el))
    return ''.join(acc)

  @staticmethod
  def node(item, **kwargs):
    LOG({'item': item})

    level = item['indent']
    if level == -1:  # toplevel
      indent = ""
    elif level == 0:
      indent = "- "
    else:
      indent = (level * "  ") + "- "

    acc = ["<pre>" + indent + RENDER.line(item['line'], indent=indent, **kwargs) + "</pre>"]
    for child in item['children']:
      acc.append(RENDER.node(child, **kwargs))

    return "".join(acc)

  @staticmethod
  def block(block, **kwargs):
    match block:
      case {'msg': _} as msg:
        return kwargs.get('render_msg', DISCUSSION_RENDER.msg)(msg)
      case {'line': line}:
        return RENDER.line(line, **kwargs)
    if block == ['']:
      return '<br/>'

    acc = []
    for item in block:
      match item:
        case {'value': _, 'indent': _, 'children': _, 'line': _}:
          acc.append(RENDER.node(item, **kwargs))
        case {'line': line}:
          acc.append('<pre>' + RENDER.line(line, **kwargs) + '</pre>')
        case _:
          assert False

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

    acc = list()
    acc.append(details)

    tags = list()
    for item in children[1:]:
      match item:
        case {'msg': _}:
          tags += TAG.gather(item['content'])
        case _:
          assert False

    for i, item in enumerate(children):
      match item:
        case {'msg': _} as msg if i == 0:
          acc.append('<summary>')
          acc.append(DISCUSSION_RENDER.msg(item, **kwargs))
          if tags:
            acc.append("<div class='tags-summary'>" + ' '.join(map(RENDER.tag,tags)) + "</div>")
          acc.append('</summary>')
        case {'msg': _}:
          acc.append(DISCUSSION_RENDER.msg(msg, msg_indent="<span class='msg_dash'><b>-</b></span>", **kwargs))
        case _:
          acc.append(RENDER.block(item, **kwargs))

    acc.append('</details>')
    return ''.join(acc)

  @staticmethod
  def section(section, **kwargs):
    # LOG({'kwargs': kwargs, 'section': section['title']})
    if 'render_section' in kwargs:
      return kwargs['render_section'](section, **kwargs)

    # if section['title'] == 'HTML':
    #   LOG({'html section': section})
    #   acc = []
    #   for block in section['blocks']:
    #     for l in block:
    #       acc.append(l)
    #   return "\n".join(acc)

    if section['title'] == 'METADATA':
      if JOURNAL.is_journal(section):
        return JOURNAL_RENDER.METADATA(FLAT.parse_metadata_from_section(section), **kwargs)

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
      bar = "".join(RENDER_UTIL.nav())
    else:
      bar = D['bar']

    result = (
      f"<!DOCTYPE hmtl>"
      f"<html><head>"
        f"<title>{D['title']}</title>"
        f"{RENDER_UTIL.STYLE()}"
        "<script src='/js/highlight-selected.js'></script>"
      "</head>"
      f"<body>"
        f"{bar}"
        f"<div class=\"content\">"
        f"<h1 class='title'>{D['title']}</h1>"
        f"<main id='main'>{D['content']}</main>"
      f"</div></body></html>"
    )
    return Response(result, mimetype="text/html")
