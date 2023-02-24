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
  def line(L, **kwargs):
    LOG(L)

    # cont is continuation
    # base is the escape function for when we have no more rendering left to do
    def parse_url(S, cont, base):
      nonlocal kwargs

      if ': ' in S:
        prefix, potentially_url = S.rsplit(': ', 1)

        if potentially_url.strip().startswith('https://'):
          return cont(prefix, base) + ": " + RENDER.link(potentially_url, **kwargs)

        if potentially_url.strip().endswith(".note") and \
           FLAT.note_id_len() == len(potentially_url.strip()):
          return cont(prefix, base) + ": " + RENDER.note(potentially_url, **kwargs)

        if potentially_url.strip().startswith('/'):
          return cont(prefix, base) + ": " + RENDER.link(potentially_url, **kwargs)

        if potentially_url.strip().startswith(FLASK_UTIL.URL_ROOT()):
          return cont(prefix, base) + ": " + RENDER.link(potentially_url, view='ref', **kwargs)

      return cont(S, base)

    def highlight_tags(S, base):
      # replace DAILY with linked DAILY and run base() on everything between
      return "<a href='/daily'><b>DAILY</b></a>".join(map(base, S.split("DAILY")))

    return parse_url(L, cont=highlight_tags, base=FLASK_UTIL.ESCAPE)


  @staticmethod
  def node(item, **kwargs):
    # LOG({'kwargs': kwargs})
    render_msg = kwargs.get('render_msg', None)
    result = None

    LOG({'item': item, 'render_msg': render_msg})

    level = item['indent']
    if level == -1:  # toplevel
      indent = ""
    elif level == 0:
      indent = "- "
    else:
      indent = (level * "  ") + "- "

    result = RENDER.line(item['value'], indent=indent, **kwargs)
    result = "<pre>" + indent + result + "</pre>"

    acc = list()
    acc.append(result)

    for child in item['children']:
      acc.append(RENDER.node(child, **kwargs))

    return "".join(acc)

  @staticmethod
  def block(block, **kwargs):
    match block:
      case {'msg': _} as msg:
        return kwargs.get('render_msg', DISCUSSION_RENDER.msg)(msg)

    if block == ['']:
      return '<br/>'

    acc = []
    for item in block:
      # if item is a tree/node
      # if isinstance(item, dict):
        # acc.append(RENDER.node(item, **kwargs))
        # continue

      if isinstance(item, str):
        line_rendered = "\n".join(map(lambda x: RENDER.line(x, **kwargs), item.split('\n')))
        acc.append(f"<pre>{line_rendered}</pre>")
        continue

      acc.append(repr(item))

    return '\n'.join(acc)

  @staticmethod
  def section(section, **kwargs):
    # LOG({'kwargs': kwargs, 'section': section['title']})
    if 'render_section' in kwargs:
      return kwargs['render_section'](section, **kwargs)

    # if section['title'] == 'entry' and \
    #    'origin_note' in kwargs and 'Tags' in FLAT.metadata(kwargs['origin_note']) and \
    #    'Journal' in FLAT.metadata(kwargs['origin_note'])['Tags']:
    #   return DISCUSSION_RENDER.section(section, **kwargs)

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
    # if section['title'] != 'entry':
    #   acc.append(f"<pre>--- {section['title']} --- </pre>")

    # don't print two empty blocks consecutively
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
      f"<!DOCTYPE hmtl><html><head>{RENDER_UTIL.STYLE()}<title>{D['title']}</title></head>"
      f"<body>"
        f"{bar}"
        f"<div class=\"content\">"
        f"<h1 class='title'>{D['title']}</h1>"
        f"<main id='main'>{D['content']}</main>"
      f"</div></body></html>"
    )
    return Response(result, mimetype="text/html")
