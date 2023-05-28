console.log("local storage for 'time_displayed'", window.localStorage.getItem('time_displayed'));
if (window.localStorage.getItem('time_displayed') === undefined) {
  window.localStorage.setItem('time_displayed', true);
}

function render_time() {
  let timestamps = document.getElementsByClassName("msg_timestamp");
  for (let timestamp of timestamps) {
    if (window.localStorage.getItem('time_displayed') === 'true') {
      timestamp.style.display = '';
    } else {
      timestamp.style.display = 'none';
    }
  }
}

function toggle_time() {
  window.localStorage.setItem('time_displayed', window.localStorage.getItem('time_displayed') === 'false');
  console.log("local storage for 'time_displayed'", window.localStorage.getItem('time_displayed'));
  render_time();
}

window.addEventListener('load', render_time);
