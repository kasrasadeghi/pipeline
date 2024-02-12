class DEVICE:
  @staticmethod
  def phone():
    return 'ANDROID_ROOT' in os.environ

  @staticmethod
  def repo_name():
    # we can run python on the phone
    if DEVICE.phone():
      return 'phone'

    return 'core'
