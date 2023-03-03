window.addEventListener('load', () => {
  console.log('enable highlight-selected');

  updateSelected = () => {
    // clear selected
    const currently_selected = document.getElementsByClassName('selected');
    for (s of currently_selected) {
      s.classList.remove('selected');
    }

    // select from hash
    if (window.location.hash) {
      const selected = document.getElementById(decodeURI(window.location.hash.slice(1)));
      selected.classList.add('selected');
    }
  };

  window.addEventListener('hashchange', () => {
    updateSelected();
  });

  updateSelected();
});
