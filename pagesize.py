@app.route('/test/pagesize')
def get_pagesize():
  # ideas:
  content = (
    """<script>
      function test_pagesize() {
        const start = performance.now();
        const path = document.getElementById('path_input').value;
        console.log('testing pagesize on ', path);

        // escapeHtml: https://stackoverflow.com/questions/6234773/can-i-escape-html-special-chars-in-javascript
        const escapeHtml = (unsafe) => {
          return unsafe.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');
        };
        fetch(path)
          .then((res) => res.text())
          .then((data) => {
             document.getElementById('url-requested').innerHTML = 'GET ' + path;
             document.getElementById('size-result').innerHTML = 'size: ' + (data.length) + ' bytes';
             document.getElementById('latency-result').innerHTML = 'result: ' + (performance.now() - start);
             document.getElementById('content-result').innerHTML = escapeHtml(data);
          })
          .catch((err) => {
             docuemnt.getElementById('content-result').innerHTML = err;
          });
      }
      window.addEventListener('load', () => {
        test_pagesize();
      });
    </script>"""
    "<input style='color:black' type=text name='path' id='path_input' value='/test/latency/ping'></input>"
    "<button style='color:black' onclick='test_pagesize()'>test pagesize and latency</button>"
    "<p id='url-requested'>result:<p>"
    "<p id='size-result'>size:<p>"
    "<p id='latency-result'>ping:<p>"
    "<pre id='content-result'></pre>"
  )
  return RENDER.base_page({'title': 'Latency Tester', 'content': content})
