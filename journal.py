class JOURNAL_RENDER:
  @staticmethod
  def METADATA(metadata, **kwargs):
    """ @param metadata - must be parsed metadata"""
    return (f"<pre>Journal for {metadata['Title']}\n"
            f"- created at {util.date_cmd('-d', metadata['Date'], '+%T %Z')}\n"
            f'- see the day <a href="/before">before</a> <a href="/after">after</a>'
            f"</pre>")

class JOURNAL:
  @staticmethod
  def is_journal(metadata_section):
    metadata = FLAT.metadata_section(metadata_section)
    return 'Tags' in metadata and "Journal" in metadata['Tags']

  @staticmethod
  def date_to_parts(date_str):
    day_of_month = util.date_cmd("-d", date_str, "+%e")
    day_of_month_suffix = {1:"st", 2:"nd", 3:"rd"}.get(int(day_of_month[-1]), "th")
    month, year = util.date_cmd("-d", date_str, "+%B %Y").split()
    title = f"{month} {day_of_month}{day_of_month_suffix}, {year}"
    return DICT(day_of_month, day_of_month_suffix, month, year, title)

  @staticmethod
  def date_to_title(date_str):
    return JOURNAL.date_to_parts(date_str).title

  @staticmethod
  def init_journal(note, D):
    with open(FLAT.to_path(note)) as f:
      content = f.read()
    with open(FLAT.to_path(note), "w") as f:
      f.write(f"# {D.month} {D.day_of_month}\n\n{content}Tags: Journal\n")
    return note

  @staticmethod
  def find_journal_for_day(date):
    return FLAT.find_note_with_title(JOURNAL.date_to_title(date))

  @staticmethod
  def create_journal_for_day(date):
    D = JOURNAL.date_to_parts(date)
    new_note = FLAT.make_new(D.title)
    JOURNAL.init_journal(new_note, D)
    return new_note

  @staticmethod
  def today():
    if note := JOURNAL.find_journal_for_day("today"):
      return note
    return JOURNAL.create_journal_for_day("today")

  @staticmethod
  def yesterday():
    if note := JOURNAL.find_journal_for_day("yesterday"):
      return note
    return JOURNAL.create_journal_for_day("yesterday")

@app.route("/journals")
def journal_list():
  return FLAT_RENDER.LIST(reversed([x for x in FLAT.list_by_create_date() if 'Tags' in FLAT.metadata(x) and "Journal" in set(FLAT.metadata(x)['Tags'].split())]),
                     title="Journals",
                     linkfunc=FLAT.to_url,
                     colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                     namefunc=FLAT.title)

@app.route("/today")
def today():
  return redirect(FLAT.to_url(JOURNAL.today(), view="disc"), code=302)

@app.route("/yesterday")
def yesterday():
  return redirect(FLAT.to_url(JOURNAL.yesterday(), view="disc"), code=302)

@app.route("/day-of/<note>")
def route_day_of(note):
  if n := JOURNAL.find_journal_for_day(FLAT.metadata(note)['Date']):
    return redirect(FLAT.to_url(n, view="disc"))

  return "ERROR: could not find journal on that day"

@app.route("/before", defaults={"note": None})
@app.route("/before/<note>")
def route_before(note):
  if not note:
    view, note = FLAT.try_from_url(request.environ['HTTP_REFERER'])

  day = util.day_before(current_day := FLAT.metadata(note)['Date'])
  if n := JOURNAL.find_journal_for_day(day):
    return redirect(FLAT.to_url(n, view=view))

  return f"ERROR: could not find journal on the day before {JOURNAL.date_to_title(current_day)}, which is {JOURNAL.date_to_title(day)}"

@app.route("/after", defaults={"note": None})
@app.route("/after/<note>")
def route_after(note):
  if not note:
    view, note = FLAT.try_from_url(request.environ['HTTP_REFERER'])

  day = util.day_after(current_day := FLAT.metadata(note)['Date'])
  if n := JOURNAL.find_journal_for_day(day):
    return redirect(FLAT.to_url(n, view=view))

  return f"ERROR: could not find journal on the day after {JOURNAL.date_to_title(current_day)}, which is {JOURNAL.date_to_title(day)}"
