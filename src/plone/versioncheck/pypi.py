# -*- coding: utf-8 -*-

from collections import namedtuple
from collections import OrderedDict
from pkg_resources import parse_version
from pkg_resources import SetuptoolsVersion
from plone.versioncheck.utils import requests_session

import datetime
import sys


PYPI_URL = 'https://pypi.python.org/pypi'


Release = namedtuple('Release', ['version', 'release_date'])


def mmbp_tuple(version):
    """major minor bugfix, postfix tuple from version

    - 1.0     -> 1.0.0.0
    - 1.2     -> 1.2.0.0
    - 1.3.4   -> 1.3.4.0
    - 1.3.4.5 -> 1.3.4.5
    """
    parts = version.base_version.split('.')
    parts += ['0'] * (4 - len(parts))
    return [int(_) for _ in parts]


def check(name, version, session):  # noqa: C901
    result = OrderedDict([
        # ('major', None),
        # ('minor', None),
        # ('bugfix', None),
        # ('majorpre', None),
        # ('minorpre', None),
        # ('bugfixpre', None),
        ('major', Release(version=u'0.0.0.0',
                          release_date=datetime.date(1970, 1, 1))),
        ('minor', Release(version=u'0.0.0.0',
                          release_date=datetime.date(1970, 1, 1))),
        ('bugfix', Release(version=u'0.0.0.0',
                           release_date=datetime.date(1970, 1, 1))),
        ('majorpre', Release(version=u'0.0.0.0',
                             release_date=datetime.date(1970, 1, 1))),
        ('minorpre', Release(version=u'0.0.0.0',
                             release_date=datetime.date(1970, 1, 1))),
        ('bugfixpre', Release(version=u'0.0.0.0',
                              release_date=datetime.date(1970, 1, 1))),
    ])

    # parse version to test against:
    try:
        version = parse_version(version)
    except TypeError:
        return False, 'Version broken/ not checkable.'
    if not isinstance(version, SetuptoolsVersion):
        return False, 'Can not check legacy version number.'
    vtuple = mmbp_tuple(version)

    # fetch pkgs json info from pypi
    url = '{0}/{1}/json'.format(PYPI_URL, name)
    resp = session.get(url)

    # check status code
    if resp.status_code == 404:
        return False, 'Package "{name}" not on pypi.'.format(name=name)
    elif resp.status_code != 200:
        return False, str(resp.status_code)
    data = resp.json()
    releases = sorted(data['releases'])
    for release in releases:
        # major check (overall)
        rel_v = parse_version(release)
        if not isinstance(rel_v, SetuptoolsVersion) or not rel_v > version:
            continue
        rel_vtuple = mmbp_tuple(rel_v)
        rel_data = data['releases'][release]
        rel_date = datetime.date(1970, 1, 1)
        for rel_pkg in rel_data:
            time_string = rel_pkg.get('upload_time')
            if time_string:
                crel_date = datetime.datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%S').date()  # NOQA: E501
                if crel_date > rel_date:
                    rel_date = crel_date
        if rel_vtuple[0] > vtuple[0]:
            if (
                rel_v.is_prerelease and
                rel_v > parse_version(result['majorpre'].version)
            ):
                result['majorpre'] = Release(version=release,
                                             release_date=rel_date)
            elif (
                not rel_v.is_prerelease and
                rel_v > parse_version(result['major'].version)
            ):
                result['major'] = Release(version=release,
                                          release_date=rel_date)
            continue
        if (  # Only compare same version line
            rel_vtuple[0] == vtuple[0] and
            rel_vtuple[1] > vtuple[1]
        ):
            if (
                rel_v.is_prerelease and
                rel_v > parse_version(result['minorpre'].version)
            ):
                result['minorpre'] = Release(version=release,
                                             release_date=rel_date)
            elif (
                not rel_v.is_prerelease and
                rel_v > parse_version(result['minor'].version)
            ):
                result['minor'] = Release(version=release,
                                          release_date=rel_date)
            continue
        if (  # Only compare same version line
            rel_vtuple[0] == vtuple[0] and
            rel_vtuple[1] == vtuple[1] and
            rel_vtuple[2] > vtuple[2]
        ):
            if (
                rel_v.is_prerelease and
                rel_v > parse_version(result['bugfixpre'].version)
            ):
                result['bugfixpre'] = Release(version=release,
                                              release_date=rel_date)
            elif (
                not rel_v.is_prerelease and
                rel_v > parse_version(result['bugfix'].version)
            ):
                    result['bugfix'] = Release(version=release,
                                               release_date=rel_date)
            continue

    # reset non existing versions
    for version_tag in result.keys():
        if result[version_tag].version == u'0.0.0.0':
            result[version_tag] = None
    # filter out older
    if (
        result['major'] and
        result['majorpre'] and
        parse_version(result['majorpre'].version) <
            parse_version(result['major'].version)
    ):
        result['majorpre'] = None
    if (
        result['minor'] and
        result['minorpre'] and
        parse_version(result['minorpre'].version) <
            parse_version(result['minor'].version)
    ):
        result['minorpre'] = None
    if (
        result['bugfix'] and
        result['bugfixpre'] and
        parse_version(result['bugfixpre'].version) <
            parse_version(result['bugfix'].version)
    ):
        result['bugfixpre'] = None

    return 2 if resp.from_cache else 1, result


def check_all(pkgsinfo, limit=None, nocache=False):
    session = requests_session(nocache=nocache)
    pkgs = pkgsinfo['pkgs']
    sys.stderr.write(
        'Check PyPI for updates of {0:d} packages.'.format(len(pkgs))
    )
    if limit:
        sys.stderr.write(' Check limited to {0:d} packages.'.format(limit))
    pkgsinfo['pypi'] = {}
    errors = []
    for idx, pkgname in enumerate(sorted(pkgs)):
        if not idx % 20 and idx != limit:
            sys.stderr.write('\n{0:4d} '.format(idx))
        current = next(iter(pkgs[pkgname]))
        state, result = check(
            pkgname,
            pkgs[pkgname][current]['v'],
            session
        )
        if not state:
            sys.stderr.write('E')
            errors.append((pkgname, pkgs[pkgname][current]['v'], str(result)))
            continue
        pkgsinfo['pypi'][pkgname] = result
        sys.stderr.write('O' if state == 1 else 'o')
        if limit and idx == limit:
            break
    for error in errors:
        sys.stderr.write(
            '\nError in {0} version {1} reason {2}'.format(
                *error
            )
        )

    sys.stderr.write('\nPyPI check finished\n')
