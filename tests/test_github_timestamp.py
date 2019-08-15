'''
Unit tests for GitHubTimestamp object
'''


import unittest
from datetime import datetime

from issyours_github.api import GitHubTimestamp


class TimestampTests(unittest.TestCase):

    def test_across(self):
        '''Check that different methods refer to the same timestamp'''
        value = {
            'datetime': datetime(2019, 12, 28, 1, 2, 3),
            'unix': 1577494923,
            'header': 'Sat, 28 Dec 2019 01:02:03 GMT',
            'isotime': '2019-12-28T01:02:03Z',
        }
        timestamp = GitHubTimestamp(value['datetime'])
        for fmt in ('unix', 'header', 'isotime'):
            with self.subTest(fmt=fmt):
                self.assertEqual(value[fmt], getattr(timestamp, fmt))


    def test_backwards(self):
        '''Check that no timezone manipulation happens within GitHubTimestamp'''
        values = (
            ('header', 'Fri, 26 Jul 2019 06:11:14 GMT'),
            ('isotime', '2018-06-12T20:02:58Z'),
            ('unix', 1564110674),
        )
        for attr, value in values:
            with self.subTest(attr=attr, value=value):
                kwargs = {attr: value}
                timestamp = GitHubTimestamp(**kwargs)
                backwards = getattr(timestamp, attr)
                self.assertEqual(value, backwards)
