function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  } else {
    let x = document.getElementById("updated-at");
    x.innerHTML = "Geolocation is not supported by this browser.";
  }
}

function showPosition(position) {
  console.log('what');
  let x = document.getElementById("updated-at");
  console.log(position);
  const {latitude, longitude} = position.coords;
  x.innerHTML = (
    `(Latitude, Longitude): (<a href="https://google.com/maps/?q=${latitude},${longitude}">${latitude}, ${longitude}</a>)`
    + `<br>at ${new Date(position.timestamp).toLocaleString()}<br>accuracy (in meters): ${position.coords.accuracy}`);
}


window.addEventListener('load', () => { load_preventing(); });
window.addEventListener('load', () => {
  console.log('hi');
  getLocation();
});

function load_preventing() {
  console.log('load_preventing');

  let preventing = window.localStorage.getItem('prevent-default');
  if (preventing === null) {
    window.localStorage.setItem('prevent-default', 'false');
    preventing = 'false';
  }
  document.getElementById('prevent-default').checked = (preventing === 'true');
  console.log('load_preventing becomes', window.localStorage.getItem('prevent-default'));

  // TODO catch local storage change event and update the checkbox
  // TODO CONSIDER maybe not, so that every instance of a page can have a different queue?  but the queues might interfere with each other, but it's probably easier to do a queue merge for local messages than it is to do something else.  hmmmmm.
}

function store_preventing() {
  window.localStorage.setItem('prevent-default', document.getElementById('prevent-default').checked);
  console.log('store_preventing becomes', window.localStorage.getItem('prevent-default'));
}

function handle_msg(event, note) {
  const form = new FormData(event.target);
  const data = Object.fromEntries(form.entries());
  console.log('handle_msg', note, ':', data);
  const text_input = event.target.firstChild;

  const preventing = window.localStorage.getItem('prevent-default');
  if (preventing === 'true') {
    event.preventDefault();
    text_input.value = '';  // clear text input

    const createID = () => {
      const now = new Date();
      // Intl.DateTimeFormat: https://tc39.es/ecma402/#sec-datetimeformat-abstracts
      const dateformat = (o) => {
        return new Intl.DateTimeFormat("en-US", o).format(now).toString();
      }
      const brief_weekday         = dateformat({weekday: 'short'});  // Sun
      const brief_month           = dateformat({month: 'short'});  // Feb
      let   nozero_day_of_month   = dateformat({day: 'numeric'});
      if (nozero_day_of_month.length === 1) {
        nozero_day_of_month = ' ' + nozero_day_of_month;  // left pad, for " 5"
      }
      // Date: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date
      const time_hour_min_sec_24h = now.toTimeString().slice(0, 8);    // 16:00:17
      const local_timezone        = now.toTimeString().slice(19, -1);  // Pacific Standard Time
      const year                  = now.getFullYear(); // 2023
      const gmt_offset            = now.toTimeString().slice(9, 17);   // GMT-0800

      const IANA_timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      return [
        `${brief_weekday}, ${brief_month} ${nozero_day_of_month} ${year}, ${time_hour_min_sec_24h} (${local_timezone}, ${gmt_offset}, ${IANA_timezone})`,
        {brief_weekday, brief_month, nozero_day_of_month, time_hour_min_sec_24h, local_timezone, year, IANA_timezone}
      ];
    };
    const [id, timeobj] = createID();

    const el = (tag, classname, children) => {
      const result = document.createElement(tag);
      if (classname !== undefined) {
        result.setAttribute('class', classname);
      }
      if (children !== undefined) {
        for (child of children) {
          result.appendChild(child);
        }
      }
      return result;
    };

    const render_msg = (msg, id) => {
      /// render message in temp queue
      const msg_content = el('div', 'msg_content');
      msg_content.innerHTML = msg;

      const msg_container = el('div', 'msg_container', [msg_content]);

      const msg_timestamp = el('a', 'msg_timestamp');
      msg_timestamp.innerHTML = timeobj.time_hour_min_sec_24h;
      msg_timestamp.setAttribute('href', '#' + id);

      const result = el('div', 'msg', [msg_timestamp, msg_container]);
      result.setAttribute('id', id);
      return result;
    };

    const message = {content: data.msg, id};

    if (data.msg.length > 0) {
      document.getElementById('message-queue').appendChild(render_msg(data.msg, id));
    }

    // TODO put message in localStorage so it doesn't get lost on refresh
    // window.localStorage.set(message);
    console.log(message);

    // TODO catch local storage change event and update the message queue

    // TODO CONSIDER maybe use local storage to sync tabs???  so we can send to the server but also have updated tabs???
    // - but having non-synced tabs is nice sometimes, to recover from failure-states.  i should probably just use git for that tho

    // scroll to bottom
    window.scrollTo(0, document.body.scrollHeight);

    // TODO scroll down to

    // fetch('/', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify(data),
    // })
    //   .then((r) => r.json())
    //   .then((data) => {
    //     // TODO reify message
    //   })
    //   .catch((error) => {
    //     // TODO wait and retry later, or present a button that enables the user to retry.
    //   });
  }
}
