from unittest import TestCase
from issyours.pelican import _increment_backrefs as increment_backrefs


class BackrefsTest(TestCase):

    test_data = (
        # before, after, increment
        (r'hello \1 \2 \\3 world', r'hello \2 \3 \\3 world', 1),
        (r'hello \1 \2 \\3 world', r'hello \11 \12 \\3 world', 10),
        (r'\1 \2 \\3 world', r'\11 \12 \\3 world', 10),
        (r'hello \1 \2', r'hello \2 \3', 1),
    )

    def test_increment_backrefs(self):
        for before, after, increment in self.test_data:
            with self.subTest(before=before, after=after, increment=increment):
                self.assertEqual(increment_backrefs(before, increment), after)
