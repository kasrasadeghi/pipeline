class JOURNAL_RENDER:
  @staticmethod
  def METADATA(metadata, **kwargs):
    """ @param metadata - must be parsed metadata"""
    return (f"<pre>Journal for {DATE.cmd('-d', metadata['Date'], '+%a')}, {metadata['Title']}\n"
            f"- created at {DATE.cmd('-d', metadata['Date'], '+%T %Z')}\n"
            f'- see the day <a href="/before">before</a> <a href="/after">after</a>'
            f"</pre>")

class JOURNAL:
  @staticmethod
  def is_journal(metadata_section):
    metadata = FLAT.parse_metadata_from_section(metadata_section)
    return 'Tags' in metadata and "Journal" in metadata['Tags']

  @staticmethod
  def date_to_title(date_str):
    # date_str -> e.g. "March 8th, 2023", e.g. "March 13rd, 2023" (lol)
    assert (x := pattern_scatter(date_str, 'WWW mmm DD HH:MM:SS ZZZ YYYY', 'WmDHMSZY')), f"'{date_str}' doesn't match pattern"
    return DATE.abbr_month_to_full(x['m']) + ' ' + x['D'].strip() + DATE.joke_ordinal_day_of_month_suffix(x['D']) + ", " + x['Y']

  @staticmethod
  def init_journal(note, D):
    with open(FLAT.to_path(note)) as f:
      content = f.read()
    with open(FLAT.to_path(note), "w") as f:
      f.write(f"# {D['month']} {D['day_of_month']}\n\n{content}Tags: Journal\n")
    return note

  @staticmethod
  def find_journal_for_day(date):
    return FLAT.find_note_with_title(JOURNAL.date_to_title(date))

  @staticmethod
  def create_journal_for_day(date):
    JOURNAL.init_journal(new_note := FLAT.make_new(JOURNAL.date_to_title(date)), D)
    return new_note

  @staticmethod
  def today():
    if note := JOURNAL.find_journal_for_day(DATE.now()):
      return note
    return JOURNAL.create_journal_for_day(DATE.now())

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

  return f"ERROR: could not find journal on {JOURNAL.date_to_title(current_day)}, which is {JOURNAL.date_to_title(day)}"

@app.route("/before")
def route_before_bare():
  view, note = FLAT.try_from_url(request.environ['HTTP_REFERER'])
  return route_before(note, view=view)

@app.route("/before/<note>")
def route_before(note, view='disc'):
  day = DATE.day_before(current_day := FLAT.metadata(note)['Date'])
  if n := JOURNAL.find_journal_for_day(day):
    return redirect(FLAT.to_url(n, view=view))

  return f"ERROR: could not find journal on the day before {JOURNAL.date_to_title(current_day)}, which is {JOURNAL.date_to_title(day)}"


@app.route("/after")
def route_after_bare():
  view, note = FLAT.try_from_url(request.environ['HTTP_REFERER'])
  return route_after(note, view=view)

@app.route("/after/<note>")
def route_after(note, view='disc'):
  day = DATE.day_after(current_day := FLAT.metadata(note)['Date'])
  if n := JOURNAL.find_journal_for_day(day):
    return redirect(FLAT.to_url(n, view=view))

  return f"ERROR: could not find journal on the day after {JOURNAL.date_to_title(current_day)}, which is {JOURNAL.date_to_title(day)}"
