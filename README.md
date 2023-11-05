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

