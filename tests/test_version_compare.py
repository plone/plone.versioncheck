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


demo_json = '''{
    "info": {},
    "releases": {
        "1.0": {},
        "1.0.1": {},
        "1.0.2": {},
        "1.0.3": {},
        "1.0.4": {},
        "1.0.5": {},
        "1.0.6": {},
        "1.0.7": {},
        "1.0.8": {},
        "1.0.9": {},
        "1.0.10": {},
        "1.0.11": {},
        "1.0.12": {},
        "1.0.13.dev0": {},
        "1.1.0": {},
        "1.1.1": {},
        "1.2.0.b1": {},
        "2.0.0": {},
        "3.0.a1": {}
    }
}
'''


assumed_demo_result = OrderedDict([
    ('major', u'2.0.0'),
    ('minor', u'1.1.1'),
    ('bugfix', u'1.0.12'),
    ('majorpre', u'3.0.a1'),
    ('minorpre', u'1.2.0.b1'),
    ('bugfixpre', u'1.0.13.dev0'),
])


@responses.activate
def test_check():
    session = requests_session(nocache=False)
    name = u'demo'
    responses.add(
        responses.GET, '{0}/{1}/json'.format(PYPI_URL, name),
        content_type='application/json',
        body=demo_json,
    )
    assert check(name, u'1.0', session) == (1, assumed_demo_result)
