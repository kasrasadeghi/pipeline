@app.route('/test/latency')
def test_latency():
  # ideas:
  # test latency to different endpoints
  # test latency from each device

  content = (
    """<script>
      function test_latency() {
        const start = performance.now();
        console.log('testing latency');
        fetch('/test/latency/ping')
          .then((res) => res.json())
          .then((data) => {
             document.getElementById('latency-result').innerHTML = 'result: ' + (performance.now() - start);
             document.getElementById('content-result').innerHTML = JSON.stringify(data, null, 2);
          });
      }
      window.onload(() => {
        test_latency();
      });
    </script>"""
    "<button style='color:black' onclick='test_latency()'>test latency</button>"
    "<p id='latency-result'>result:<p>"
    "<pre id='content-result'></pre>"
  )
  return RENDER.base_page({'title': 'Latency Tester', 'content': content})

@app.route('/test/latency/ping')
def test_latency_ping():
  return {'result': 'pong'}
