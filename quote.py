class QUOTE:
  @staticmethod
  def message(note, timestamp_id):
    page = REWRITE.note(note)
    for section in page:
      if 'roots' in section:
        for root in section['roots']:
          if 'children' in root:
            for child in root['children']:
              if 'date' in child and child['date'] == timestamp_id:
                return child
      if 'blocks' in section:
        for block in section['blocks']:
          if 'date' in block and block['date'] == timestamp_id:
            return block

    return None
