mkdir ~/notes
cd ~/notes

# big hack to make pipeline's index page work
if ! [ -f 4e0ce4ff-1663-49f9-8ced-30f91202ae08.note ]; then
  echo '--- METADATA ---' > 4e0ce4ff-1663-49f9-8ced-30f91202ae08.note
  echo 'Date:' $(date '+%a %b %e %T %Z %Y') \
                      >> 4e0ce4ff-1663-49f9-8ced-30f91202ae08.note
  echo 'Title: index' >> 4e0ce4ff-1663-49f9-8ced-30f91202ae08.note
  echo 'Tags: index'  >> 4e0ce4ff-1663-49f9-8ced-30f91202ae08.note
fi
