'''
Data classes to be used across Issyours project
'''


import re
from datetime import datetime

import attr
from attr.validators import instance_of, optional

from issyours.reader import ReaderBase



@attr.s
class DataItem:
    '''
    All data items are expected to contain a reference to their parent Reader
    and to be freezable (able to be made read-only) after populating them with
    values.
    '''

    reader = attr.ib(validator=instance_of(ReaderBase))
    _frozen = False
    _required = ()


    def freeze(self):
        '''Make this object read-only'''
        self.validate()
        self._frozen = True


    def validate(self):
        '''Validate object before turning it readonly'''
        # Missing values
        missing = set()
        for field in self._required:
            if not getattr(self, field):
                missing.add(field)
        if missing:
            raise ValueError('required fields are not filled: {}'\
                             .format(', '.join(sorted(missing))))

        # Type correctness: TODO


    def __setattr__(self, attr, value):
        if self._frozen:
            raise AttributeError('attributes were made read-only for this {}'.format(self.__class__.__name__))
        else:
            super().__setattr__(attr, value)


    def __delattr__(self, attr):
        if self._frozen:
            raise AttributeError('attributes were made read-only for this {}'.format(self.__class__.__name__))

        else:
            super().__delattr__(attr)



class Person:
    pass


class IssueComment:
    pass


class IssueEvent:
    pass


@attr.s
class IssueLabel:
    name = attr.ib(type=str)
    color = attr.ib(type=str)

    _color_regex = re.compile(r'^#[0-9a-f]{6}$', re.IGNORECASE)

    @color.validator
    def check_color_format(self, attribute, value):
        if not self._color_regex.match(value):
            raise ValueError('color must be valid RGB hex string starting with #')



@attr.s
class Issue(DataItem):
    uid         = attr.ib()
    author      = attr.ib(default=None, validator=optional(instance_of(Person)))
    status      = attr.ib(default='')
    title       = attr.ib(default='')
    body        = attr.ib(default='')
    url         = attr.ib(default='')
    labels      = attr.ib(default=attr.Factory(list))
    assignees   = attr.ib(default=attr.Factory(list))
    # TODO: attr.s does not run validators from __setattr__, only from __init__
    created_at  = attr.ib(default=None, validator=optional(instance_of(datetime)))
    modified_at = attr.ib(default=None, validator=optional(instance_of(datetime)))
    fetched_at  = attr.ib(default=None, validator=optional(instance_of(datetime)))
    closed_at   = attr.ib(default=None, validator=optional(instance_of(datetime)))

    _required = ('reader', 'uid', 'author', 'status', 'title', 'created_at')
