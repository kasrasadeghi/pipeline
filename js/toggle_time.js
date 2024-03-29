console.log("local storage for 'time_displayed'", window.localStorage.getItem('time_displayed'));
if (window.localStorage.getItem('time_displayed') === undefined) {
  window.localStorage.setItem('time_displayed', true);
}


let init_time_displayed = window.localStorage.getItem('time_displayed') === 'true';
function init_time_display() {
  let timestamps = document.getElementsByClassName("msg_timestamp");
  for (let timestamp of timestamps) {
    if (init_time_displayed) {
      timestamp.style.display = '';
    } else {
      timestamp.style.display = 'none';
    }
  }
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

render_time();
