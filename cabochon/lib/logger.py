from datetime import datetime

class Logger:
    def __init__(self, filename):
        self.file = open(filename, "a")

    def __call__(self, message):
        now = datetime.now()
        print >> self.file, "%s %s" % (now, message)
        self.file.flush()
