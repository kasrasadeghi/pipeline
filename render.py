# a context and hook management system, using kwargs-style hooks like RENDER below
class CONTEXT:
  @staticmethod
  def DEFAULT(kwargs, key):
    """ return a copy with the given key removed """
    default = dict(kwargs)
    if key in default:
      del default[key]
    return default

# the tree renderer
class RENDER:
  @staticmethod
  def link(url, **kwargs):
    return f'<a href="{url}">{url}</a>'

  @staticmethod
  def note(note, **kwargs):
    return f'<a href="{FLAT.to_url(note, view="disc")}">{note}</a>'

  @staticmethod
  def node(item, **kwargs):
    render_msg = kwargs.get('render_msg', None)
    result = None

    level = item['indent']
    if level == -1:  # toplevel
      indent = ""
    elif level == 0:
      indent = "- "
    else:
      indent = (level * "  ") + "- "

    if DISCUSSION.is_msg(item):
      if render_msg:
        return render_msg(item)
      else:
        return DISCUSSION_RENDER.msg(item)

    if item['value'].startswith('link: '):
      url = item['value'].removeprefix('link: ')
      result = f'<pre>{indent}link: {RENDER.link(url)}</pre>'
      debug("link:", repr(item), debugmode='RENDER LINK')

    if item['value'].startswith('note: '):
      note = item['value'].removeprefix('note: ').strip()
      result = f"<pre>{indent}note: {RENDER.note(note)}</pre>"

    if None == result:
      debug('item, but none matched:', repr(item), debugmode='RENDER')
      result = "<pre>" + indent + str(escape(item['value'])) \
        + (": " if item['children'] and not item['value'].strip().endswith(':') else "") \
        + "</pre>"

    acc = list()
    acc.append(result)

    for child in item['children']:
      acc.append(RENDER.node(child))

    return "".join(acc)

  @staticmethod
  def section(section, **kwargs):
    if 'render_section' in kwargs:
      return kwargs['render_section'](section, **kwargs)

    acc = list()
    if section['section'] != 'entry':
      acc.append(f'<pre>--- {section["section"]} --- </pre>')

    if section['section'] == 'DISCUSSION':
      return DISCUSSION_RENDER.section(section)

    if section['section'] == 'METADATA':
      if JOURNAL.is_journal(section):
        return JOURNAL_RENDER.METADATA(FLAT.metadata_section(section))

    # don't print two empty blocks consecutively
    for block in TREE.blocks_from_section(section):

      if block == ['']:
        debug("whitespace")
        acc.append('<br/>')
        continue

      for item in block:
        # if item is a tree/node
        if isinstance(item, dict):
          acc.append(RENDER.node(item))
          continue

        if isinstance(item, str):
          acc.append(f"<pre>{item}</pre>")
          debug("string:", item)
          continue

        acc.append(repr(item))

    return '\n'.join(acc)

  @staticmethod
  def page(note, sections, **kwargs):
    return '\n'.join(map(lambda x: RENDER.section(x, **kwargs), sections)) + TREE.filesize(note)

  @staticmethod
  def root(note, **kwargs):
    content = RENDER.page(note, PARSER.parse_file(FLAT.to_path(note)), **kwargs)

    bar = FLAT_RENDER._bar(note,
                           f'<a href="/disc/{note}">disc</a>'
                           )

    # compose html
    title = FLAT.title(note)
    result = (
      f"<div class=\"msgbox\" style='font-feature-settings: \"liga\" 0'>"
      f"{content}</div>"
      f'<form method="post"><input class="msg_input" autocomplete="off" autofocus type="text" name="msg"></form>'
    )
    return RENDER.base_page(DICT(title, bar, content=result))


  @staticmethod
  def base_page(D):
    """
    D is a magic_dict with keys: { title, bar, content }
    bar=None renders the default bar with RENDER_UTIL.nav()

    USAGE:
    - RENDER.base_page(DICT(title, bar, content))
    - RENDER.base_page(DICT(title, bar, content=result))
    - RENDER.base_page(DICT(title, content, bar=None))
    """
    if D.bar is None or D.bar == "":
      bar = "".join(RENDER_UTIL.nav())
    else:
      bar = D.bar

    result = (
      f"<!DOCTYPE hmtl><html><head>{RENDER_UTIL.STYLE()}<title>{D.title}</title></head>"
      f"<body>{bar}<div class=\"content\">"
        f'<h1 class="title">{D.title}</h1>'
        f"{D.content}"
      f"</div></body></html>"
    )
    return Response(result, mimetype="text/html")
