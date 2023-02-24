# DEPENDS ON journal.py

class PLAN_RENDER:
  @staticmethod
  def section(section, **kwargs):
    if section['title'] == 'METADATA':
      return RENDER.section(section, **CONTEXT.DEFAULT(kwargs, 'render_section'))

    if section['title'] != 'entry':
      return ''

    msg_blocks = list()
    for block in section['blocks']:
      if not DISCUSSION.block_is_msg(block):
        continue

      if "DAILY" in block[0]['value']:
        msg_blocks.append(block)

    def render_msg(msg_block, date_prefix=''):
      return DISCUSSION_RENDER.msg(msg_block[0], timerender=lambda x: date_prefix + util.date_cmd("-d", x, "+%T"))

    import itertools  # repeat
    todo = [{'isDone': False, 'block': item}
            for item in filter(lambda x: "ADD" in x[0]['value'], msg_blocks)]
    done = [{'startedWhen': None, 'block': item}
            for item in filter(lambda x: "DONE" in x[0]['value'], msg_blocks)]
    rest = [{'startedWhen': None, 'block': item}
            for item in filter(lambda x: "DONE" not in x[0]['value'] and "ADD" not in x[0]['value'], msg_blocks)]

    dangling_done = list()
    for d in done:
      done_msg = d['block'][0]['value'].removeprefix("msg: ")
      task = done_msg.split("DAILY DONE:", 1)[1]  # get what's after DAILY DONE:
      corresponding_todo_msg = "DAILY ADD:" + task

      found = False
      for t in todo:
        if corresponding_todo_msg in t['block'][0]['value']:
          found = True
          t['isDone'] = True
          d['startedWhen'] = DISCUSSION.date(t['block'][0])

      if not found:
        dangling_done.append(d)

    undone_todos = list(filter(lambda y: not y['isDone'], todo))
    undangling_done = list(filter(lambda y: y['startedWhen'] is not None, done))

    def render_todos(title, l):
      if l:
        return f"<pre>{title}:</pre>" + "".join(map(lambda x: render_msg(x['block']), l))
      else:
        return ""

    return (render_todos("TODO", undone_todos)
            + render_todos("DONE", undangling_done)
            + render_todos("DANGLING DONE", dangling_done)
            + render_todos("MISC", rest))

@app.route('/daily', defaults={"note": None})
@app.route('/daily/<note>')
def get_plan_note(note):
  if not note:
    _, note = FLASK_UTIL.REFERER_NOTE()
    return redirect(FLAT.to_url(note, view='daily'))

  DEBUG.init_state()
  return DISCUSSION_RENDER.MAIN(note, render_section=PLAN_RENDER.section)
