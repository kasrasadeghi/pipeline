class REF:
  @staticmethod
  def parse_ref(url):
    if not url.startswith(FLASK_UTIL.URL_ROOT()):
      LOG({'ERROR while parsing ref': url, 'step': '(1) url root parsing failure'})
      return url
    url = url.removeprefix(FLASK_UTIL.URL_ROOT())

    if not url.startswith('disc/'):
      LOG({'ERROR while parsing ref': url, 'step': '(2) not a link to a disc'})
      return url
    url = url.removeprefix('disc/')

    if not len(url) > FLAT.note_id_len():
      LOG({'ERROR while parsing ref': url, 'step': '(3) not long enough to contain a note uuid'})

    note, rest = url[:FLAT.note_id_len()], url[FLAT.note_id_len():]
    if not FLAT.check_is_note(note):
      LOG({'ERROR while parsing ref': url, 'step': f'(4) check that \'{note}\' is a note'})
      return url

    return note + rest  # chop off the '#' part of the id of the note
