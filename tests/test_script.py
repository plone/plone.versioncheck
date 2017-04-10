# -*- coding: utf-8 -*-

from plone.versioncheck.script import run

import pytest
import sys


help_output = '''
usage: py.test [-h] [-p] [-n] [-N] [-r] [-d] [-i] [-m] [--no-cache] [-b]
               [-o [OUTPUT]] [--no-colors] [--debug-limit DEBUG_LIMIT]
               [buildout]

Fetch information about pinned versions and its overrides in simple and complex/cascaded buildouts.

positional arguments:
  buildout              path to buildout.cfg or other *.cfg file

optional arguments:
  -h, --help            show this help message and exit
  -p, --pypi            check PyPI for newer versions
  -n, --newer           display only packages with newer version than active
  -N, --newer-orphaned  display orphaned packages only when newer versions
                        available
  -r, --required-by     show information about requirements (only if tracking
                        file is available)
  -d, --show-release-dates
                        show information about release dates (only for package
                        lookup from PyPI)
  -i, --ignore-tracking
                        ignore tracking file (if present)
  -m, --machine         show as machine readable output (json)
  --no-cache            do not use a cache for PyPI
  -b, --browser         show as html for webbrowser
  -o [OUTPUT], --output [OUTPUT]
                        safe output to output-file
  --no-colors           do not show colors
  --debug-limit DEBUG_LIMIT
                        Limit the number of PyPI versions fetched for
                        debugging

States and color codes:
  [A]ctive (white)
  [D]evelop (green)
  [O]rphaned (magenta)
  [I]nherited (older or same versions are gray, newer are yellow)
  [U]pdate of final release on PyPI available (cyan)
  [P]rerelease update on PyPI available (blue)
  [X] unpinned (red)
  [r] Requirement (gray)
  [a] Annotation (gray)

Color of package name helps to indicate overall state of a package.
'''  # NOQA: E501


def test_script_help(capsys):
    with pytest.raises(SystemExit):
        sys.argv = ['versioncheck', '--help']
        result = run()
        out, err = capsys.readouterr()
        assert result is None
        assert out == help_output


json_output = '''{
"collective.quickupload": {
    "versions": [
        {
            "description": "foo.cfg",
            "version": "1.5.8",
            "annotation": "",
            "state": "A"
        },
        {
            "description": "baz.cfg",
            "version": "1.5.2",
            "annotation": "",
            "state": "I"
        }
    ],
    "state": "A"
},
"ipython": {
    "versions": [
        {
            "description": "buildout.cfg",
            "version": "5.3.0",
            "annotation": "",
            "state": "A"
        }
    ],
    "state": "A"
},
"lazy": {
    "versions": [
        {
            "description": "buildout.cfg",
            "version": "1.0",
            "annotation": "",
            "state": "A"
        }
    ],
    "state": "A"
},
"products.cmfcore": {
    "versions": [
        {
            "description": "buildout.cfg",
            "version": "2.1.1",
            "annotation": "Just a Test Case\nwith multiple lines",
            "state": "A"
        },
        {
            "description": "bar.cfg",
            "version": "2.2.0",
            "annotation": "",
            "state": "In"
        },
        {
            "description": "foo.cfg",
            "version": "3.0.1",
            "annotation": "",
            "state": "In"
        },
        {
            "description": "baz.cfg",
            "version": "2.2.10",
            "annotation": "",
            "state": "In"
        }
    ],
    "state": "In"
}
}
'''


def test_script_machine(capsys):
    sys.argv = ['versioncheck', '-m']
    result = run()
    out, err = capsys.readouterr()
    assert result is None
    # assert out == json_output


def test_script_browser(capsys):
    sys.argv = ['versioncheck', '-b']
    result = run()
    out, err = capsys.readouterr()
    assert result is None
    # assert out = browser_output


def test_script_pypi(capsys):
    sys.argv = ['versioncheck', '-p']
    result = run()
    out, err = capsys.readouterr()
    assert result is None
    # assert out = browser_output


def test_script_ignore_tracking(capsys):
    sys.argv = ['versioncheck', '-i']
    result = run()
    out, err = capsys.readouterr()
    assert result is None
    # assert out = browser_output


def test_script_ignore_tracking_pypi(capsys):
    sys.argv = ['versioncheck', '-p', '-i']
    result = run()
    out, err = capsys.readouterr()
    assert result is None
    # assert out = browser_output
