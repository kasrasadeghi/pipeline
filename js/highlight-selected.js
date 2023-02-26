window.addEventListener('load', () => {
  if (window.location.hash === '') {
    return;
  }
  const selected = document.getElementById(decodeURI(window.location.hash.slice(1)));
  selected.classList.add('selected');
  console.trace('load selected', selected);

  console.log(document);

  for (e of document.getElementsByClassName('msg_timestamp')) {
    e.addEventListener('click', (event) => {
      const currently_selected = document.getElementsByClassName('selected');
      for (s of currently_selected) {
        s.classList.remove('selected');
      }
      event.target.parentElement.classList.add('selected');
    });
  }
});
