'''Logging setup'''


import logging
import os


class ShyLogHandler(logging.StreamHandler):
    '''
    A log handler that emits messages only if root logger has no other handlers
    '''

    root = logging.getLogger()

    def emit(self, record):
        if not self.root.hasHandlers():
            super().emit(record)



def setup():
    package = 'issyours'
    log = logging.getLogger(package)

    if not log.hasHandlers():
        handler = ShyLogHandler()
        handler.setLevel(logging.DEBUG)
        log.addHandler(handler)

    if os.environ.get('ISSYOURS_DEBUG'):
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARNING)


setup()
