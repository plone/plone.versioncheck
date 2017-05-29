# -*- coding: utf-8 -*-

from collections import OrderedDict
from plone.versioncheck.parser import nostdout
from plone.versioncheck.parser import parse


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


def test_parse(capsys):
    input = 'buildout.cfg'

    result = parse(input, False)
    out, err = capsys.readouterr()
    assert err[:23] == "Parsing buildout files:"
    assert """buildout.cfg
  3 entries in versions section.
  1 entries in annotations section.
""" in err

    assert result == {
        'collective.quickupload': OrderedDict([
            ('foo.cfg', {'v': '1.5.8', 'a': ''}),
            ('baz.cfg', {'v': '1.5.2', 'a': ''})
        ]),
        'ipython': OrderedDict([('buildout.cfg', {'v': '5.3.0', 'a': ''})]),
        'lazy': OrderedDict([
            ('buildout.cfg', {'v': '1.0', 'a': ''}),
            ('spam.cfg', {'v': '>= 1.1', 'a': ''})
        ]),
        'products.cmfcore': OrderedDict([
            ('buildout.cfg', {'v': '2.1.1', 'a': '\nJust a Test Case\nwith multiple lines'}),  # NOQA: E501
            ('bar.cfg', {'v': '2.2.0', 'a': ''}),
            ('foo.cfg', {'v': '3.0.1', 'a': ''}),
            ('baz.cfg', {'v': '2.2.10', 'a': ''})
        ]),
    }
