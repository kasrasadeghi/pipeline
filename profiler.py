# NOTE this file cannot be called "profile.py" because python won't be able to distinguish it from the builtin 'profile' module
# see: https://github.com/google/ci_edit/issues/192#issuecomment-517118503

@app.route('/api/profile-dumps')
def get_profile_targets():
  dumps = os.listdir('profile-dumps')
  get_timestamp = lambda x: x.rsplit('.', 2)[1]
  dumps.sort(key=get_timestamp)
  dumps.reverse()

  prefix = request.args.get('prefix', default='')

  acc = []
  duration_acc = []
  for filename in dumps:
    if not filename.startswith(prefix):
      continue
    ms = filename.rsplit('.', 3)[1].removesuffix('ms') # get the milliseconds duration
    duration_acc.append(int(ms))
    LOG({'filename': filename})
    acc.append(f"     <option value='{filename}'>{get_timestamp(filename)}: {filename}</option>")
  return {'options': "\n".join(acc), 'average': sum(duration_acc[:10]) / len(duration_acc[:10])}

@app.route('/api/profile-dump/<dump>')
def get_profile_target(dump):
  filename = os.path.join('profile-dumps', dump)

  # pstats to string: https://stackoverflow.com/questions/51536411/saving-cprofile-results-to-readable-external-file
  import io
  outputstream = io.StringIO()
  import pstats
  p = pstats.Stats(filename, stream=outputstream)
  p.sort_stats('tottime')
  p.print_stats()
  p.sort_stats('cumulative')
  p.print_callers()
  p.print_callees()
  return FLASK_UTIL.ESCAPE(outputstream.getvalue())

@app.route('/test/profile')
def get_profile_data_viewer():
  # ideas:
  content = (
    """<script>
      document.addEventListener('load', () => {
        let url = new URL(window.location);
        url.searchParams.set('profile');
        document.getElementById('select-profile').value = url.href;
      });
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
        let url = new URL('/api/profile-dumps', window.location.origin);
        const prefix = document.getElementById('prefix').value;
        url.searchParams.set('prefix', prefix);
        fetch(url.href)
          .then((res) => res.json())
          .then((data) => {
             document.getElementById('select-profile').innerHTML = data['options'];
             document.getElementById('profile-average').innerHTML = data['average'];
          })
          .catch((err) => {
             document.getElementById('content-result').innerHTML = err;
          });
        event.preventDefault();
      }
      function clear_profile_folder() {
        // TODO
        refresh_profiles();
        event.preventDefault();
      }
    </script>"""
    "<form>"
      "<select id='select-profile' name='profile-target'>"
      + get_profile_targets()['options'] + \
      "</select>"
      "<br/>"
      "<input type=button value='get profile' onclick='get_profile()'></input>"
    "</form>"
    "<form>"
      "<label for='prefix' value='filter prefix'></label>"
      "<input type=text value='' id='prefix' onsubmit='refresh_profiles()()'></input>"
      "<input type=button value='refresh profile targets' onclick='refresh_profiles()'></input>"
    "</form>"
    "<p id='profile-requested'>no result yet<p>"
    "<p id='profile-average'>no average time yet<p>"
    "<pre id='content-result'></pre>"
  )
  return RENDER.base_page({'title': 'Profiler Output', 'content': content})
