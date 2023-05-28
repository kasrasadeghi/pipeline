let time_displayed = true;

function toggle_time() {
  let timestamps = document.getElementsByClassName("msg_timestamp");
  time_displayed = !time_displayed;
  for (let timestamp of timestamps) {
    if (time_displayed) {
      timestamp.style.display = '';
    } else {
      timestamp.style.display = 'none';
    }
  }
}
