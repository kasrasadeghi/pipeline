# pipeline
pipeline is a message-based notes system for iterative reflection.

you can run it locally, or you can run it over a vpn.
i use wireguard to run it on my phone and my computers at home.

as a software package, pipeline is a simple flask app.
it uses the ~/notes folder in your home directory,
and populates it with a flat set of `[uuid].note` files.
each note has messages in it, human-readable in a custom plain-text format.

# core modules
the setup script (WIP) creates an index file for you in ~/notes.
you can visit this with https://localhost:5000/ or http://localhost:5000/.

otherwise, you can go to https://localhost:5000/today or http://localhost:5000/today,
and see a new journal note created for each day.
