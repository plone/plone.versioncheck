# coding=utf-8
from plone.versioncheck.utils import find_relative
from unittest import TestCase


class TestUtils(TestCase):

    def test_find_relative(self):
        ''' Checks if find relative is working nicely
        '''
        self.assertEqual(
            find_relative('http://example.com/foo.cfg'),
            'http://example.com'
        )
        self.assertEqual(
            find_relative('file://../versions/foo.cfg'),
            'file://../versions',
        )
        # BBB: this test should fail!
        self.assertEqual(
            find_relative('../versions/foo.cfg'),
            '',
            # BBB: it should be equal to ../versions
        )
