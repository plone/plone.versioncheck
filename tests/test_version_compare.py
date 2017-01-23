# -*- coding: utf-8 -*-
from collections import OrderedDict
from pkg_resources import parse_version
from pkg_resources import SetuptoolsVersion
from plone.versioncheck.pypi import check
from plone.versioncheck.pypi import mmbp_tuple
from plone.versioncheck.pypi import PYPI_URL
from plone.versioncheck.utils import requests_session

import responses


def test_mmbp_tuple():
    assert mmbp_tuple(parse_version(u'0.0.0.0')) == [0, 0, 0, 0]
    assert mmbp_tuple(parse_version(u'1.0')) == [1, 0, 0, 0]
    assert mmbp_tuple(parse_version(u'1.1.0')) == [1, 1, 0, 0]
    assert mmbp_tuple(parse_version(u'0.1')) == [0, 1, 0, 0]
    assert mmbp_tuple(parse_version(u'0.10.1')) == [0, 10, 1, 0]
    assert mmbp_tuple(parse_version(u'1.1.1.1')) == [1, 1, 1, 1]
    assert mmbp_tuple(parse_version(u'1.1.0.a1')) == [1, 1, 0, 0]


@responses.activate
def test_check():
    session = requests_session(nocache=False)
    name = u'demo'
    responses.add(
        responses.GET, '{0}/{1}/json'.format(PYPI_URL, name),
        content_type='application/json',
        body='{ "info": {}, "releases": { "1.0": {} }}'
    )
    assumed_result = OrderedDict([
        ('major', None),
        ('minor', None),
        ('bugfix', None),
        ('majorpre', None),
        ('minorpre', None),
        ('bugfixpre', None),
    ])
    assert check(name, u'1.0', session) == (1, assumed_result)
