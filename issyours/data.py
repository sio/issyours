'''
Data classes to be used across Issyours project
'''


import re
from datetime import datetime

import attr
from attr.validators import instance_of, optional

from issyours.reader import ReaderBase



@attr.s(frozen=True)
class Person:
    reader = attr.ib(validator=instance_of(ReaderBase))



@attr.s(frozen=True)
class IssueComment:
    pass



@attr.s(frozen=True)
class IssueEvent:
    pass



@attr.s(frozen=True)
class IssueLabel:
    name = attr.ib(type=str)
    color = attr.ib(type=str)

    _color_regex = re.compile(r'^#[0-9a-f]{6}$', re.IGNORECASE)

    @color.validator
    def check_color_format(self, attribute, value):
        if not self._color_regex.match(value):
            raise ValueError('color must be valid RGB hex string starting with #')



@attr.s(frozen=True)
class Issue:
    '''
    Contents of individual issue.
    Note: attachments() call must return a sequence of stream-like objects
    '''
    reader      = attr.ib(validator=instance_of(ReaderBase))
    uid         = attr.ib()
    author      = attr.ib(default=None, validator=optional(instance_of(Person)))
    status      = attr.ib(default='')
    title       = attr.ib(default='')
    body        = attr.ib(default='')
    url         = attr.ib(default='')
    labels      = attr.ib(factory=list)
    assignees   = attr.ib(factory=list)
    created_at  = attr.ib(default=None, validator=optional(instance_of(datetime)))
    modified_at = attr.ib(default=None, validator=optional(instance_of(datetime)))
    fetched_at  = attr.ib(default=None, validator=optional(instance_of(datetime)))
    closed_at   = attr.ib(default=None, validator=optional(instance_of(datetime)))
    attachments = attr.ib(default=list)

    @attachments.validator
    def check_if_callable(self, attribute, value):
        if not callable(value):
            raise ValueError('{!r} must be a callable that accepts zero arguments'.format(
                attribute.name
            ))
