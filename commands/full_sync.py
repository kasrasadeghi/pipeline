@COMMAND.REGISTER('SYNC')
def COMMAND_SYNC(args, continuation, redirect_page):
  if arg := args['arg']:
    continuation(arg)
  else:
    continuation('')

  output = FLAT.cmd(['git add *.note'], shell=True)

  redirect_page('/git/commit?message=FULL-SYNC')
