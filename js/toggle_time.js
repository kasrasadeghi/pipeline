let time_displayed = true;

if (window.localStorage.getItem('time_displayed') !== undefined) {
  time_displayed = window.localStorage.getItem('time_displayed');
}

function toggle_time() {
  let timestamps = document.getElementsByClassName("msg_timestamp");
  time_displayed = !time_displayed;
  window.localStorage.setItem('time_displayed', time_displayed);
  for (let timestamp of timestamps) {
    if (time_displayed) {
      timestamp.style.display = '';
    } else {
      timestamp.style.display = 'none';
    }
  }
}
