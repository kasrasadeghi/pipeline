function tvbrightnessup() {
  fetch('/event/tv_brightness_up', {method: 'POST'});
}

function tvbrightnessdown() {
  fetch('/event/tv_brightness_down', {method: 'POST'});
}
