class YOUTUBE_DL:
  folder = '/home/kasra/pipeline-ytdl-cache'
  cmd = 'yt-dlp'

  @classmethod
  def DOWNLOAD(cls, url, title):
    import os
    import subprocess

    # go to the twitch clip folder
    cwd = os.getcwd()
    os.chdir(cls.folder)

    # cache the files beforehand
    pre = os.listdir()

    # download the twitch clip
    p = subprocess.run([cls.cmd, url], capture_output=True, text=True)

    # figure out what file was downloaded, if any
    post = os.listdir()

    # show a bar if they're both there
    output = p.stdout + "\n---\n" + p.stderr + '\n'
    if not p.stdout or not p.stderr:
      output = p.stdout + p.stderr + '\n'

    if diff := set(post) - set(pre):
      LOG({"ytdl diff": diff})
      assert len(diff) == 1
      filename = next(iter(diff))
    else:
      return output

    # append to the mappings file
    with open(cls.folder + '/mapping.json') as f:
      data = json.load(f)

    data['list'].append({'title': title, 'url': url, 'filename': filename})

    with open(cls.folder + '/mapping.json', 'w') as f:
      json.dump(data, f, indent=2)

    os.chdir(cwd)
    return output


@COMMAND.REGISTER('YTDL')  # works with twitch clips
def COMMAND_YTDL(args, continuation, redirect_page):

  rest = args['arg']

  if rest.strip().startswith("http"):
    title, url = 'title not given', args['arg']
  else:
    title, url = rest.rsplit(': ', 1)

  import subprocess
  import os

  LOG({'downloading twitch clip': url})

  output = YOUTUBE_DL.DOWNLOAD(url, title)
  continuation(args['arg'])
  FLAT.append_to_note(args['origin'], output)
