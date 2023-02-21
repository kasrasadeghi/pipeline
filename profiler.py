# NOTE this file cannot be called "profile.py" because python won't be able to distinguish it from the builtin 'profile' module
# see: https://github.com/google/ci_edit/issues/192#issuecomment-517118503

@app.route('/api/profile-dumps', defaults={'profile_dir': 'profile-dumps'})
@app.route('/api/saved-profile-dumps', defaults={'profile_dir': 'saved-profile-dumps'})
def get_profile_targets(profile_dir='profile-dumps'):
  dumps = os.listdir(profile_dir)
  print(profile_dir)
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
  return {'options': "\n".join(acc), 'average': 0 if len(acc) == 0 else sum(duration_acc[:10]) / len(duration_acc[:10])}

@app.route('/api/profile-dump/<dump>')
def get_profile_target(dump):
  if request.args.get('saved', 'false') == 'true':
    filename = os.path.join('saved-profile-dumps', dump)
  else:
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

@app.route('/api/clear-unsaved-profiles')
def clear_unsaved_profiles():
  assert util.basename(os.getcwd()) == 'notes-website', f"'{os.getcwd()}' is not 'notes-website'"
  assert 'profile-dumps' in os.listdir()
  import subprocess
  subprocess.run('rm profile-dumps/*', shell=True)
  return 'DONE'

@app.route('/api/save-profile/<dump>')
def save_profile_target(dump):
  filename = os.path.join('profile-dumps', dump)
  destination = os.path.join('saved-profile-dumps', dump)

  import shutil
  shutil.copy2(filename, destination)  # copy and preserve metadata
  return 'DONE'

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
        const use_saved = document.getElementById('use-saved').checked;
        console.log('getting profile dump ', path);

        let url = new URL(window.location);
        url.searchParams.set('profile', path);
        window.history.pushState({}, '', url);

        let query = new URL('/api/profile-dump/' + path, window.location.origin);
        query.searchParams.set('saved', use_saved);
        fetch(query.href)
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
      function save_profile() {
        const selected_profile = document.getElementById('select-profile').value;
        const use_saved = document.getElementById('use-saved').checked;

        let url = new URL(window.location);
        url.searchParams.set('profile', selected_profile);
        url.searchParams.set('saved', use_saved);
        window.history.pushState({}, '', url);
        fetch('/api/save-profile/' + selected_profile)
          .then((res) => res.text())
          .then((data) => {
            if (data === 'DONE') { alert('successfully saved profile'); }
            refresh_profiles();
            get_profile();
          })
        event.preventDefault();
      }
      function refresh_profiles() {
        const use_saved = document.getElementById('use-saved').checked;
        const prefix = document.getElementById('prefix').value;

        const route = use_saved ? '/api/saved-profile-dumps' : '/api/profile-dumps';
        let url = new URL(route, window.location.origin);
        url.searchParams.set('prefix', prefix);

        let new_history = new URL(window.location);
        new_history.searchParams.set('prefix', prefix);
        new_history.searchParams.set('saved', use_saved);
        window.history.pushState({}, '', new_history);

        fetch(url.href)
          .then((res) => res.json())
          .then((data) => {
             document.getElementById('select-profile').innerHTML = data['options'];
             document.getElementById('profile-average').innerHTML = data['average'];
          });
        if (event) {
          event.preventDefault();
        }
      }
      function clear_profiles() {
        fetch('/api/clear-unsaved-profiles')
          .then((res) => res.text())
          .then((data) => {
             if (data === 'DONE') { alert('successfully cleared unsaved profiles'); }
             refresh_profiles();
          });
        event.preventDefault();
      }
    </script>"""
    "<form>"
      "<select id='select-profile' name='profile-target'>"
      + get_profile_targets()['options'] + \
      "</select>"
      "<br/>"
      "<input type=button value='get profile' onclick='get_profile()'></input>"
      "<input type=button value='save profile' onclick='save_profile()'></input>"
    "</form>"
    "<form>"
      "<label for='prefix'>filter prefix</label>"
      "<input type=text value='' id='prefix' onsubmit='refresh_profiles()()'></input>"
      "<input type=button value='refresh profile targets' onclick='refresh_profiles()'></input>"
      "<input type=button value='clear unsaved profiles' onclick='clear_profiles()'></input>"
      "<div style='margin: 0.5rem'>"
        "<label for='use-saved'>only saved profiles</label>"
        "<input type=checkbox id='use-saved'>"
      "</div>"
    "</form>"
    "<p id='profile-requested'>no result yet<p>"
    "<p id='profile-average'>no average time yet<p>"
    "<pre id='content-result'></pre>"
  )
  return RENDER.base_page({'title': 'Profiler Output', 'content': content})
