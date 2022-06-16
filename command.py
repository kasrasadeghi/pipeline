class COMMAND:
  handlers = dict()

  @staticmethod
  def REGISTER(command_name):
    def register(handler):
      COMMAND.handlers[command_name] = handler
      return handler
    return register

  @staticmethod
  def PARSE(note, message):
    # NOTE: return True if we didn't run anything

    # a command must start with \
    if not message.startswith('\\'):
      return True

    end_of_cmd = message.find(' ')
    if end_of_cmd == -1:
      # no argument
      cmd = message[1:]
      argument = None
    else:
      # unary argument:
      # have a space to separate the \COMMAND and its argument,
      # - which is the rest of the string
      cmd = message[1:end_of_cmd]
      argument = message[end_of_cmd + 1:]

    if cmd not in COMMAND.handlers:
      return True

    def continuation(handler_result):
      form = dict()
      new_message = '\\' + cmd + ' ' + handler_result
      form['msg'] = new_message
      FLAT.handle_msg(note, form)

    args = dict()
    args['arg'] = argument
    args['origin'] = note

    handler = COMMAND.handlers[cmd]
    handler(args, continuation)

    return False
