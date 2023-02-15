window.addEventListener('load', () => { load_preventing(); });

function load_preventing() {
  console.log('load_preventing');

  let preventing = window.localStorage.getItem('prevent-default');
  if (preventing === null) {
    window.localStorage.setItem('prevent-default', 'false');
    preventing = 'false';
  }
  document.getElementById('prevent-default').checked = (preventing === 'true');
  console.log('load_preventing becomes', window.localStorage.getItem('prevent-default'));
}

function store_preventing() {
  window.localStorage.setItem('prevent-default', document.getElementById('prevent-default').checked);
  console.log('store_preventing becomes', window.localStorage.getItem('prevent-default'));
}

function handle_msg(event, note) {
  const form = new FormData(event.target);
  const data = Object.fromEntries(form.entries());
  console.log('handle_msg', note, ':', data);

  const preventing = window.localStorage.getItem('prevent-default');
  if (preventing === 'true') {
    event.preventDefault();

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

      const IANA_timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      return [
        `${brief_weekday}, ${brief_month} ${nozero_day_of_month} ${year}, ${time_hour_min_sec_24h} (${local_timezone})`,
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

      const timestamp_link = el('a');
      timestamp_link.innerHTML = timeobj.time_hour_min_sec_24h;
      timestamp_link.setAttribute('href', '#' + id);

      const msg_timestamp = el('div', 'msg_timestamp', [timestamp_link]);

      const result = el('div', 'msg', [msg_timestamp, msg_container]);
      result.setAttribute('id', id);
      return result;
    };

    if (data.msg.length > 0) {
      document.getElementById('message-queue').appendChild(render_msg(data.msg, id));
    }

    // TODO put message in localStorage so it doesn't get lost on refresh
    // scroll down

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
