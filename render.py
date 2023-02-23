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
  def block(block, **kwargs):
    acc = []
    for item in block:
      if item.value == 'line':
      # if isinstance(item, str):
        line_rendered = RENDER.line(item.get(), **kwargs)
        acc.append(f"<pre>{line_rendered}</pre>")
      else:
        acc.append(repr(item))

    return '\n'.join(acc)

  @staticmethod
  def line(L, **kwargs):
    return L

  @staticmethod
  def node(item, **kwargs):
    level = item.at('indent')
    if level == -1:  # toplevel
      indent = ""
    elif level == 0:
      indent = "- "
    else:
      indent = (level * "  ") + "- "

    acc = list()
    acc.append("<pre>" + RENDER.line(item.value, **kwargs) + "</pre>")

    for child in item:
      if isinstance(child, str):
        acc.append(RENDER.line(child))
      else:
        acc.append(RENDER.node(child, **kwargs))

    return item.format()

  @staticmethod
  def section(section, **kwargs):
    # LOG({'kwargs': kwargs, 'section title': section['title']})
    if 'render_section' in kwargs:
      return kwargs['render_section'](section, **kwargs)

    if section['title'] == 'entry' and \
       'origin_note' in kwargs and 'Tags' in FLAT.metadata(kwargs['origin_note']) and \
       'Journal' in FLAT.metadata(kwargs['origin_note'])['Tags']:
      return DISCUSSION_RENDER.section(section, **kwargs)

    # if section['title'] == 'DISCUSSION':
    #   return DISCUSSION_RENDER.section(section, **kwargs)

    # if section['title'] == 'HTML':
    #   LOG({'html section': section})
    #   acc = []
    #   for block in section['blocks']:
    #     for l in block:
    #       acc.append(l)
    #   return "\n".join(acc)

    # if section['title'] == 'METADATA':
    #   if JOURNAL.is_journal(section):
    #     return JOURNAL_RENDER.METADATA(FLAT.parse_metadata_from_section(section), **kwargs)

    acc = list()
    acc.append(f"<pre>--- {section['title']} --- </pre>")

    for tree in section['trees']:
      if tree.value == 'msg':
        acc.append(DISCUSSION_RENDER.msg(tree, **kwargs))
      elif tree.value == 'block':
        acc.append(RENDER.block(tree, **kwargs))
      elif tree.value == 'newline':
        acc.append('<br>')
      else:
        acc.append(repr(tree))

    return "\n".join(acc)

  @staticmethod
  def page(note, page, **kwargs):
    kwargs['origin_note'] = note
    return '\n'.join(map(lambda x: RENDER.section(x, **kwargs), page)) + TREE.filesize(note)

  @staticmethod
  def content(note, **kwargs):
    page = PARSER.parse_file(FLAT.to_path(note))
    page = TEXP_REWRITE.page(page)
    return RENDER.page(note, page, **kwargs)

  @staticmethod
  def base_page(D):
    """ D is a dict with keys: { title, bar, content } """
    if 'bar' not in D or D['bar'] is None or D['bar'] == "":
      bar = "".join(RENDER_UTIL.nav())
    else:
      bar = D['bar']

    result = (
      f"<!DOCTYPE hmtl><html><head>{RENDER_UTIL.STYLE()}<title>{D['title']}</title></head>"
      f"<body>"
        f"{bar}"
        f"<div class=\"content\">"
        f"<h1 class='title'>{D['title']}</h1>"
        f"<main id='main'>{D['content']}</main>"
      f"</div></body></html>"
    )
    return Response(result, mimetype="text/html")
