@app.route('/test/pagesize')
def get_pagesize():
  # ideas:
  content = (
    """<script>
      window.addEventListener('load', () => {
        let url = new URL(window.location);
        let path = url.searchParams.get('url');
        if (path)
          document.getElementById('path_input').value = path;
        test_pagesize();
      });

      function test_pagesize() {
        const start = performance.now();
        const path = document.getElementById('path_input').value;
        console.log('testing pagesize on ', path);

        // escapeHtml: https://stackoverflow.com/questions/6234773/can-i-escape-html-special-chars-in-javascript
        const escapeHtml = (unsafe) => {
          return unsafe.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');
        };
        let url = new URL(window.location);
        url.searchParams.set('url', path);
        window.history.pushState({}, '', url);
        fetch(path)
          .then((res) => res.text())
          .then((data) => {
             document.getElementById('url-requested').innerHTML = 'GET ' + path;
             document.getElementById('size-result').innerHTML = 'size: ' + (data.length) + ' bytes';
             document.getElementById('latency-result').innerHTML = 'result: ' + (performance.now() - start);
             document.getElementById('content-result').innerHTML = escapeHtml(data);
          })
          .catch((err) => {
             document.getElementById('content-result').innerHTML = err;
          });
        event.preventDefault();
      }

      function huh() {
        console.log('huh');
      }
    </script>"""
    "<form onsubmit='test_pagesize()'>"
      "<input type=text style='color:black' name='path' id='path_input' value='/test/latency/ping'></input>"
      "<br/>"
      "<input type=submit style='color:black' value='test pagesize and latency'></input>"
    "</form>"
    "<p id='url-requested'>result:<p>"
    "<p id='size-result'>size:<p>"
    "<p id='latency-result'>ping:<p>"
    "<pre id='content-result'></pre>"
  )
  return RENDER.base_page({'title': 'Latency Tester', 'content': content})
