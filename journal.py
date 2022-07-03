class JOURNAL_RENDER:
  @staticmethod
  def METADATA(metadata):
    """ @param metadata - must be parsed metadata"""
    return (f"<pre>Journal for {metadata['Title']}\n"
            f"- created at {util.date_cmd('-d', metadata['Date'], '+%T %Z')}\n"
            f'- see the day <a href="/before">before</a> <a href="/after">after</a>'
            f"</pre>")

class JOURNAL:
  @staticmethod
  def is_journal(metadata_section):
    parsed_metadata = TREE.parse_metadata(metadata_section)
    return 'Tags' in parsed_metadata and "Journal" in parsed_metadata['Tags']

  @staticmethod
  def date_to_parts(date_str):
    day_of_month = check_output(["date", "-d", date_str, "+%e"]).decode('latin-1').strip()
    day_of_month_suffix = {1:"st", 2:"nd", 3:"rd"}.get(int(day_of_month[-1]), "th")
    month, year = check_output(["date", "-d", date_str, "+%B %Y"]).decode('latin-1').rstrip().split()
    title = f"{month} {day_of_month}{day_of_month_suffix}, {year}"
    return DICT(day_of_month=day_of_month,
                day_of_month_suffix=day_of_month_suffix,
                month=month,
                year=year,
                title=title)

  @staticmethod
  def date_to_title(date_str):
    return JOURNAL.date_to_parts(date_str).title

@app.route("/journals")
def journal_list():
  return FLAT_RENDER.LIST(reversed([x for x in FLAT.list_by_create_date() if 'Tags' in FLAT.metadata(x) and "Journal" in set(FLAT.metadata(x)['Tags'].split())]),
                     title="Journals",
                     linkfunc=FLAT.to_url,
                     colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                     namefunc=FLAT.title)

@app.route("/today")
def today():
  return redirect(FLAT.to_disc_url(FLAT.today()), code=302)

@app.route("/yesterday")
def yesterday():
  return redirect(FLAT.to_disc_url(FLAT.yesterday()), code=302)

@app.route("/day-of/<note>")
def route_day_of(note):
  journal_title = JOURNAL.date_to_title(FLAT.metadata(note)['Date'])

  # look for a note
  for n in FLAT.list():
    if journal_title == FLAT.title(n):
      return redirect(FLAT.to_disc_url(n))

  return "ERROR: could not find journal on that day"

@app.route("/before/<note>")
def route_before(note):
  day_before_title = JOURNAL.date_to_title(util.day_before(FLAT.metadata(note)['Date']))

  # look for a note
  for n in FLAT.list():
    if day_before_title == FLAT.title(n):
      return redirect(FLAT.to_disc_url(n))

  return "ERROR: could not find journal on the day before"

@app.route("/after/<note>")
def route_after(note):
  day_after_title = JOURNAL.date_to_title(util.day_after(FLAT.metadata(note)['Date']))

  # look for a note
  for n in FLAT.list():
    if day_after_title == FLAT.title(n):
      return redirect(FLAT.to_disc_url(n))

  return "ERROR: could not find journal on the day after"

@app.route("/before")
def route_before_bare():
  note = FLAT.try_from_url(request.environ['HTTP_REFERER'])
  journal_title = JOURNAL.date_to_title(util.day_before(FLAT.metadata(note)['Date']))

  # look for a note
  for n in FLAT.list():
    if journal_title == FLAT.title(n):
      return redirect(FLAT.to_disc_url(n))

  return "ERROR: could not find journal on the day before, which was: " + journal_title

@app.route("/after")
def route_after_bare():
  note = FLAT.try_from_url(request.environ['HTTP_REFERER'])
  journal_title = JOURNAL.date_to_title(util.day_after(FLAT.metadata(note)['Date']))

  # look for a note
  for n in FLAT.list():
    if journal_title == FLAT.title(n):
      return redirect(FLAT.to_disc_url(n))

  return "ERROR: could not find journal on the day after, which was: " + journal_title
