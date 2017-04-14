# -*- coding: utf-8 -*-

from collections import OrderedDict
from plone.versioncheck.analyser import is_cfg_newer
from plone.versioncheck.analyser import is_pypi_newer
from plone.versioncheck.pypi import Release

import datetime


def test_is_cfg_newer():
    pkginfo = {}
    assert is_cfg_newer(pkginfo) is None

    pkginfo = OrderedDict([('foo.cfg', {'a': '',
                                        'release_date': datetime.date(1970, 1, 1),  # NOQA: E501
                                        'v': '1.0.0'}),
                           ('baz.cfg', {'a': '',
                                        'release_date': datetime.date(1970, 1, 1),  # NOQA: E501
                                        'v': '1.0.5'})
                           ]),
    # assert is_cfg_newer(pkginfo) == True


def test_is_pypi_newer():
    pypiinfo = OrderedDict([('major', None),
                            ('minor', None),
                            ('bugfix', None),
                            ('majorpre', None),
                            ('minorpre', None),
                            ('bugfixpre', None)])
    assert is_pypi_newer(pypiinfo) is False

    pypiinfo = OrderedDict([('major', Release(version=u'1.0.0', release_date=datetime.date(1970, 1, 1))),  # NOQA: E501
                            ('minor', None),
                            ('bugfix', None),
                            ('majorpre', None),
                            ('minorpre', None),
                            ('bugfixpre', None)])
    assert is_pypi_newer(pypiinfo) == 'pypifinal'

    pypiinfo = OrderedDict([('major', None),
                            ('minor', Release(version=u'1.1.0', release_date=datetime.date(1970, 1, 1))),  # NOQA: E501
                            ('bugfix', None),
                            ('majorpre', None),
                            ('minorpre', None),
                            ('bugfixpre', None)])
    assert is_pypi_newer(pypiinfo) == 'pypifinal'

    pypiinfo = OrderedDict([('major', None),
                            ('minor', None),
                            ('bugfix', Release(version=u'1.1.1', release_date=datetime.date(1970, 1, 1))),  # NOQA: E501
                            ('majorpre', None),
                            ('minorpre', None),
                            ('bugfixpre', None)])
    assert is_pypi_newer(pypiinfo) == 'pypifinal'

    pypiinfo = OrderedDict([('major', None),
                            ('minor', None),
                            ('bugfix', None),
                            ('majorpre', Release(version=u'2.0.0.a1', release_date=datetime.date(1970, 1, 1))),  # NOQA: E501
                            ('minorpre', None),
                            ('bugfixpre', None)])
    assert is_pypi_newer(pypiinfo) == 'pypiprerelease'

    pypiinfo = OrderedDict([('major', None),
                            ('minor', None),
                            ('bugfix', None),
                            ('majorpre', None),
                            ('minorpre', Release(version=u'1.2.0.a1', release_date=datetime.date(1970, 1, 1))),  # NOQA: E501
                            ('bugfixpre', None)])
    assert is_pypi_newer(pypiinfo) == 'pypiprerelease'

    pypiinfo = OrderedDict([('major', None),
                            ('minor', None),
                            ('bugfix', None),
                            ('majorpre', None),
                            ('minorpre', None),
                            ('bugfixpre', Release(version=u'1.1.2.a1', release_date=datetime.date(1970, 1, 1)))])  # NOQA: E501
    assert is_pypi_newer(pypiinfo) == 'pypiprerelease'
