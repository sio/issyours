'''Logging setup'''


import logging
import os


package = 'issyours'
log = logging.getLogger(package)

if not log.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)

if os.environ.get('ISSYOURS_DEBUG'):
    log.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.WARNING)

del(handler)
del(package)
