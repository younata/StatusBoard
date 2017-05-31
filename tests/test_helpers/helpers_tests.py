import unittest

from nose.tools import eq_

from tests.test_helpers.helpers import contains_


class HelpersTests(unittest.TestCase):
    @staticmethod
    def test_contains_throws_if_b_not_in_a():
        a = "aooga"
        b = "nope"

        try:
            contains_(a, b)
            raise AssertionError("_contains no work")
        except AssertionError as e:
            eq_(e.args[0], "%r not in %r" % (b, a))

    @staticmethod
    def test_contains_passes_if_b_in_a():
        a = "aooga"
        b = "oo"

        contains_(a, b)

    @staticmethod
    def test_contains_passes_if_b_is_a():
        a = "foo"
        b = "foo"

        contains_(a, b)
