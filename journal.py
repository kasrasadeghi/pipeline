class JOURNAL:
  @staticmethod
  def date_to_parts(date_str):
    day_of_month = check_output(["date", "-d", date_str, "+%e"]).decode('latin-1').strip()
    day_of_month_suffix = {1:"st", 2:"nd", 3:"rd"}.get(int(day_of_month[-1]), "th")
    month, year = check_output(["date", "-d", date_str, "+%B %Y"]).decode('latin-1').rstrip().split()
    title = f"{month} {day_of_month}{day_of_month_suffix}, {year}"
    return {"day_of_month": day_of_month,
            "day_of_month_suffix": day_of_month_suffix,
            "month": month,
            "year": year,
            "title": title}

  @staticmethod
  def date_to_title(date_str):
    return JOURNAL.date_to_parts(date_str)['title']

@app.route("/journals")
def journal_list():
  return FLAT_RENDER.LIST(reversed([x for x in FLAT.list_by_create_date() if 'Tags' in FLAT.metadata(x) and "Journal" in set(FLAT.metadata(x)['Tags'].split())]),
                     title="Journals",
                     linkfunc=FLAT.to_url,
                     colsfunc=lambda x: (FLAT.metadata(x)['Date'],),
                     namefunc=FLAT.title)

@app.route("/today")
def today():
  return redirect(FLAT.to_url(FLAT.to_disc(FLAT.today())), code=302)

@app.route("/yesterday")
def yesterday():
  return redirect(FLAT.to_url(FLAT.to_disc(FLAT.yesterday())), code=302)

@app.route("/before/<note>")
def route_before(note):
  day_before_title = JOURNAL.date_to_title(util.day_before(FLAT.metadata(note)['Date']))

  # look for a note
  for n in FLAT.list():
    if day_before_title == FLAT.title(n):
      return redirect(FLAT.to_url(FLAT.to_disc(n)))

  return "ERROR: could not find note before"

@app.route("/after/<note>")
def route_after(note):
  day_after_title = JOURNAL.date_to_title(util.day_after(FLAT.metadata(note)['Date']))

  # look for a note
  for n in FLAT.list():
    if day_after_title == FLAT.title(n):
      return redirect(FLAT.to_url(FLAT.to_disc(n)))

  return "ERROR: could not find note after"
