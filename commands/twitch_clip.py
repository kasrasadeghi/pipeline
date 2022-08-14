class TWITCH_CLIP:
  folder = '/home/kasra/twitch-clip-cache'

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
    p = subprocess.run(['youtube-dl', url], capture_output=True, text=True)

    # figure out what file was downloaded, if any
    post = os.listdir()

    # show a bar if they're both there
    output = p.stdout + "\n---\n" + p.stderr + '\n'
    if not p.stdout or not p.stderr:
      output = p.stdout + p.stderr + '\n'

    if diff := set(post) - set(pre):
      LOG({"twitch clip diff": diff})
      assert len(diff) == 1
      filename = next(iter(diff))
    else:
      return output

    # append to the mappings file
    with open(cls.folder + '/mapping.txt', 'a') as f:
      f.write(url + '\n')
      f.write(filename + '\n')
      f.write(title + '\n\n')

    os.chdir(cwd)
    return output


@COMMAND.REGISTER('TWITCH-CLIP')
def COMMAND_TWITCH_CLIP(args, continuation):

  rest = args['arg']

  if rest.strip().startswith("http"):
    title, url = 'title not given', args['arg']
  else:
    title, url = rest.rsplit(': ', 1)

  import subprocess
  import os

  LOG({'downloading twitch clip': url})

  output = TWITCH_CLIP.DOWNLOAD(url, title)
  continuation(args['arg'])
  FLAT.append_to_note(args['origin'], output)
