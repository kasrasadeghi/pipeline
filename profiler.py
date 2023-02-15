# NOTE this file cannot be called "profile.py" because python won't be able to distinguish it from the builtin 'profile' module
# see: https://github.com/google/ci_edit/issues/192#issuecomment-517118503

@app.route('/api/profile-dumps')
def get_profile_targets():
  dumps = os.listdir('profile-dumps')
  get_timestamp = lambda x: x.rsplit('.', 2)[1]
  dumps.sort(key=get_timestamp)
  dumps.reverse()

  acc = []
  for filename in dumps:
    acc.append(f"     <option value='{filename}'>{get_timestamp(filename)}: {filename}</option>")
  return "\n".join(acc)

@app.route('/api/profile-dump/<dump>')
def get_profile_target(dump):
  filename = os.path.join('profile-dumps', dump)

  # pstats to string: https://stackoverflow.com/questions/51536411/saving-cprofile-results-to-readable-external-file
  import io
  outputstream = io.StringIO()
  import pstats
  p = pstats.Stats(filename, stream=outputstream)
  p.strip_dirs()
  p.sort_stats(-1)
  p.print_stats()
  return outputstream.getvalue()

@app.route('/test/profile')
def get_profile_data_viewer():
  # ideas:
  content = (
    """<script>
      function get_profile() {
        const path = document.getElementById('select-profile').value;
        console.log('getting profile dump ', path);

        let url = new URL(window.location);
        url.searchParams.set('profile', path);
        window.history.pushState({}, '', url);
        fetch('/api/profile-dump/' + path)
          .then((res) => res.text())
          .then((data) => {
             document.getElementById('profile-requested').innerHTML = 'loaded ' + path;
             document.getElementById('content-result').innerHTML = data;
          })
          .catch((err) => {
             document.getElementById('content-result').innerHTML = err;
          });
        event.preventDefault();
      }
      function refresh_profiles() {
        // TODO
        event.preventDefault();
      }
      function clear_profiles() {
        // TODO
        refresh_profiles();
        event.preventDefault();
      }
    </script>"""
    "<form>"
      "<select id='select-profile' name='profile-target'>"
      + get_profile_targets() + \
      "</select>"
      "<br/>"
      "<input type=button value='get profile' onclick='get_profile()'></input>"
      "<input type=button value='refresh profile targets' onclick='refresh_profiles()'></input>"
      "<input type=button value='clear profiles folder' onclick='clear_profiles()'></input>"
    "</form>"
    "<p id='profile-requested'>result:<p>"
    "<pre id='content-result'></pre>"
  )
  return RENDER.base_page({'title': 'Profiler Output', 'content': content})
