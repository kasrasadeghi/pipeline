function handle_msg(event) {
  console.log('handle message, event:', event);

  const form = new FormData(event.target);
  console.log('handle message, form data:', form);

  console.log('handle message, msg: ', form.get('msg'));

  const data = Object.fromEntries(form.entries());

  // event.preventDefault();
}
