
class RemarkableNoteManager:
  root = "/home/kasra/projects/remarkable-kaz"

  def _temp(self, filename):
    return self.root + "/temp/" + filename

  def namemap(self):
    with open(self._temp("namemap.data")) as f:
      namemap = json.load(f)
      uuidmap = {v: k for k, v in namemap.items()}
      return (namemap, uuidmap)

  def notebooks(self):
    with open(self._temp("notebooks.data")) as f:
      return json.load(f)

  def copied_uuids(self):
    return [x[:-len(".metadata")] for x in os.listdir("temp") if x.endswith("metadata")]

  def pages(self):
    result = dict()
    for notebook_uuid in self.copied_uuids():
      with open(self._temp(f"{notebook_uuid}.content")) as f:
        data[notebook_uuid] = json.load(f)["pages"]
    return result

RM = RemarkableNoteManager()

@app.route("/rm/")
def get_rm_root():
  with open(f"/home/kasra/projects/remarkable-kaz/dist/index.html") as f:
    return Response(f.read(), mimetype="html")

@app.route("/rm/<rm>")
def get_rm(rm):
  with open(f"/home/kasra/projects/remarkable-kaz/dist/{rm}") as f:
    if rm.endswith("html"):
      return Response(f.read(), mimetype="html")
    return Response(f.read(), mimetype="image/svg+xml")
