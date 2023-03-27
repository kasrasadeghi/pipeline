class REWRITE_RESULT:
  @staticmethod
  def block_is_msg(block):
    return isinstance(block, dict) and 'date' in block and 'msg' in block

class REWRITE:
  @staticmethod
  def line(line):
    """ link recognition in lines
          string -> [line_content...]
          where line_content is one of:
            str
            {tag}
            {cmd}
            {link,linktype}
          and the link comes at the end
    """
    def parse_url(S):
      if ': ' in S:
        prefix, url = S.rsplit(': ', 1)
        url = url.strip()

        if url.endswith(".note") and \
           FLAT.note_id_len() == len(url.strip()):
          url = {'linktype': 'note', 'link': url}

        elif url.startswith('/'):
          url = {'linktype': 'root-link', 'link': url}

        elif url.startswith('https://') or url.startswith('http://'):
          from urllib.parse import urlparse

          # treat all 192.* and 10.* links as links to somewhere within the notes system
          parsed_url = urlparse(url)
          origin = parsed_url.netloc
          if origin.startswith('192.') or origin.startswith('10.'):
            url = {'linktype': 'internal-link', 'link': parsed_url}
          else:
            url = {'linktype': 'link', 'link': url}

        if isinstance(url, dict):
          return TAG.parse(prefix) + [url]
        else:
          return TAG.parse(S)

      return TAG.parse(S)

    return parse_url(line)

  @staticmethod
  def node(node):
    """ node: """
    return node | {'line': REWRITE.line(node['value']),
                   'children': [REWRITE.node(child) for child in node['children']]}

  @staticmethod
  def block(block):
    """ block:
          single node i.e. [node] -> [node] | msg{msg,content,date}
          single newline, identity
          for [items...]
            str -> line
            node{value,indent,children} ->node{value,indent,children,_line_}  // added line
    """
    match block:
      case [{ "value": content, "indent": 0, "children": [
              { "value": date, "indent": 1, "children": []}
           ]}] if content.startswith('msg: ') and date.startswith('Date: '):
        return {'msg': REWRITE.line(content.removeprefix('msg: ')), 'content': content, 'date': date.removeprefix('Date: ')}
      case ['']:
        return block

    acc = list()
    for item in block:
      match item:
        case {'value': _, 'indent': _, 'children': _}:
          acc.append(REWRITE.node(item))
        case str():
          acc.append({'line': REWRITE.line(item)})
        case _:
          assert False
    return acc

  @staticmethod
  def discussion_section(section):
    """ check discussion section.  if so: {title,blocks} -> {title,roots} """
    disc_section = section['title'] == 'DISCUSSION'
    journal_disc_section = (
      section['title'] == 'entry' and
      'note' in g.rewrite_note and
      'Tags' in FLAT.metadata(g.rewrite_note) and
      'Journal' in FLAT.metadata(g.rewrite_note)['Tags']
    )

    if not (disc_section or journal_disc_section):
      return section

    # handle discussion sections
    roots = [{'root': 'pre_roots', 'children': list()}]

    for block in section['blocks']:
      match block:
        case {'msg': _} as msg:
          if msg['content'].startswith("msg: - "):
            msg['msg'][0] = msg['msg'][0].removeprefix('- ')
            roots[-1]['children'].append(msg)
          else:  # new root
            roots.append({'root': 'nonfinal', 'children': [msg]})

        case _:
          roots[-1]['children'].append(block)

    if roots[-1]['root'] == 'nonfinal':  # final-able, i.e. not pre_roots
      roots[-1]['root'] = 'final'

    section = section | {'roots': roots}
    del section['blocks']
    return section

  @staticmethod
  def section(section):
    """ section.keys
          {title,blocks} -> {title,roots} | {title,blocks}
          {title,lines} identity
    """
    if 'blocks' not in section:
      assert section['title'] == 'METADATA'
      return section

    new_blocks = list()
    prev_is_msg = False
    for block in section['blocks']:
      block = REWRITE.block(block)
      if prev_is_msg and TREE.is_newline(block):
        prev_is_msg = False
        continue
      new_blocks.append(block)
      prev_is_msg = REWRITE_RESULT.block_is_msg(block)

    section = section | {'blocks': new_blocks}
    return REWRITE.discussion_section(section)

  @staticmethod
  def page(page):
    """ traverse: page -> section """
    return [REWRITE.section(section) for section in page]

  @staticmethod
  def note(note):
    page = PARSER.parse_file(FLAT.to_path(note))
    g.rewrite_note = note
    result = REWRITE.page(page)
    g.rewrite_note = dict()
    return result

@app.route('/api/parse/<note>')
def api_parse(note):
  page = PARSER.parse_file(FLAT.to_path(note))
  return {'note': note, 'page': page}

@app.route('/api/rewrite/<note>')
def get_rewrite(note):
  result = REWRITE.note(note)
  return {'note': note, 'rewrite': result}
