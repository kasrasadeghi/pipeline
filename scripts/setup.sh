# DESC: an example setup script for installing pipeline on fresh ubuntu 22.04
# - tested may 14th, 2023

## package installation

sudo apt install git make python3-pip
pip install --user flask gunicorn

# add ~/.local/bin to path if not already added, for flask/gunicorn/ other pip installs
# https://unix.stackexchange.com/questions/217622/add-path-to-path-if-not-already-in-path
if [[ ":$PATH:" != *":$HOME/.local/bin:" ]]; then
  echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
fi

## prepare ~/notes folder

mkdir ~/notes
if ! [ -f ~/notes/notes_config.json ]; then
  cp ~/pipeline/scripts/example_notes_config.json ~/notes/notes_config.json
fi

cd ~/notes

# big hack to make pipeline's index page work
if ! [ -f 4e0ce4ff-1663-49f9-8ced-30f91202ae08.note ]; then
  echo '--- METADATA ---' > 4e0ce4ff-1663-49f9-8ced-30f91202ae08.note
  echo 'Date:' $(date '+%a %b %e %T %Z %Y') \
                      >> 4e0ce4ff-1663-49f9-8ced-30f91202ae08.note
  echo 'Title: index' >> 4e0ce4ff-1663-49f9-8ced-30f91202ae08.note
  echo 'Tags: index'  >> 4e0ce4ff-1663-49f9-8ced-30f91202ae08.note
fi

## run pipeline

# gunicorn -w 1 'pipeline:app'
# could also 'make open' in pipeline/
