
try:
    import magic
    AUTODETECT = True
except ImportError, e:
    #if sys.platform == 'darwin':
    raise ImportError('Please install libmagic')
    AUTODETECT = False


class Detector(object):

    def __init__(self):
        if AUTODETECT:
            self.magic = magic.Magic(mime_encoding=True)
        else:
            self.magic = False

    def detect(self, filepath):
        if self.magic:
            encoding = self.magic.from_file(filepath)
            return encoding
        return None
