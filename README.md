# pipeline
Pipeline is a message-based notes system for iterative reflection.

You can run it locally, or you can run it over a vpn.
I use wireguard to run it on my phone when I'm out and on my computers when I'm
at home.

As a software package, pipeline is a simple flask app.
It uses the ~/notes folder in your home directory,
and populates it with a flat set of `[uuid].note` files.
Each note has messages in it, human-readable in a custom plain-text format.

# install/setup
The setup script (WIP) creates an index file for you in ~/notes.
you can visit this with https://localhost:5000/ or http://localhost:5000/.

Otherwise, you can go to https://localhost:5000/today or http://localhost:5000/today,
and see a new journal note created for each day.

I recommend making `<ip>:5000/today` your home page and using it as your central
console.

# branch REVIEW

Date: Sat Nov  4 11:38:56 PDT 2023

This is a release of pipeline to set aside old values and ambitions and embrace
a new direction.
Pipeline in this release reflects the way that is being left behind.
I might return to this branch, but for now, I'm going to try rebuilding fresh.

This pipeline was built to allow people to make their own notes systems.
This is the simplest way I know how to build a notes system that is usable for
me.

> MOTTO The code _is_ the product.

It was made iteratively.
When i could add something that takes relatively little code and drastically
improves the end result, I did.
Sometimes I'd add something that was too annoying to maintain, so I'd abandon
it, often removing it completely, but usually stashing it in `modules/` or
`experiments/`.

`experiments/` are ideas about how to change fundamentals in pipeline or to test
out new core features.  `modules/` are add-ons layered on top of the core
features.  There are also `tools/`, made to aide in developing pipeline from
within.  Its crowning achievement is a profiler integrating with werkzeug's
python-profiler integration.

## the future

The new branch will tear away Flask and will abandon the MOTTO "The code _is_
the product."  Pipeline `core-nojs` is meant for other people to dig into, to
inspire, to serve as a foundation for notes systems in general, for people
frustrated with Notion or Google Docs and wondering if they could make something
better.

Great work was put into having a simple synchronization model, as a more
sophisticated sync model would add great complexity to the codebase.  It would
require a lot of JavaScript I was unfamiliar with, and yet more unknown
unknowns.  This pipeline has a relatively simple synchronization model: every
request is sent to the same computer, which acts as a server, and immediately
writes new messages to disk.  Even in catastrophic circumstances like a power
outage, the message would probably survive.

More sophisticated synchronization will allow for an offline mode, and
in general JavaScript will allow for a significantly more responsive and dynamic
client design.  I'm also exploring making a mobile app to explore designs
outside of the limitations of js/html on mobile.
