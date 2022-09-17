@COMMAND.REGISTER('NEW-NOTE')
def COMMAND_NEW_NOTE(args, continuation, redirect_page):
  title = args['arg']

  note = FLAT.make_new(title.strip())

  result = title + ': ' + note
  continuation(result)
