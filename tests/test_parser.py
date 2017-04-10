# -*- coding: utf-8 -*-

from plone.versioncheck.parser import nostdout

import pytest


def test_nostdout(capsys):
    print('Test stdout')
    out, err = capsys.readouterr()
    assert out == 'Test stdout\n'
    with nostdout():
        print('This should never be in stdout ')

    out, err = capsys.readouterr()
    assert out == ''

    print('This should be printed again.')
    out, err = capsys.readouterr()
    assert out == 'This should be printed again.\n'
