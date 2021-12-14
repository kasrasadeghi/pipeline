@app.route("/journals")
def journal_list():
  return RENDER.LIST(reversed([x for x in FLAT.list_by_create_date() if 'Tags' in FLAT.metadata(x) and "Journal" in set(FLAT.metadata(x)['Tags'].split())]),
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
