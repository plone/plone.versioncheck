# -*- coding: utf-8 -*-
from collections import OrderedDict
from pkg_resources import parse_version
from pkg_resources import SetuptoolsVersion
from plone.versioncheck.utils import requests_session
import sys


PYPI_URL = "https://pypi.python.org/pypi"


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


def check(name, version, session):
    result = OrderedDict([
        ('major', None),
        ('minor', None),
        ('bugfix', None),
        ('majorpre', None),
        ('minorpre', None),
        ('bugfixpre', None),
    ])

    # parse version to test against:
    try:
        version = parse_version(version)
    except TypeError:
        return False, "Version broken/ not checkable."
    if not isinstance(version, SetuptoolsVersion):
        return False, "Can not check legacy version number."
    vtuple = mmbp_tuple(version)

    # fetch pkgs json info from pypi
    url = "{0}/{1}/json".format(PYPI_URL, name)
    resp = session.get(url)

    # TODO check status code
    if resp.status_code != 200:
        return False, str(resp.status_code)
    data = resp.json()
    releases = sorted(data['releases'].keys())
    for release in releases:
        # major check (overall)
        rel_v = parse_version(release)
        if not isinstance(rel_v, SetuptoolsVersion) or not rel_v > version:
            continue
        rel_vtuple = mmbp_tuple(rel_v)
        if rel_vtuple[0] > vtuple[0]:
            if rel_v.is_prerelease:
                result['majorpre'] = release
            else:
                result['major'] = release
            continue
        if rel_vtuple[1] > vtuple[1]:
            if rel_v.is_prerelease:
                result['minorpre'] = release
            else:
                result['minor'] = release
            continue
        if rel_vtuple[2] > vtuple[2]:
            if rel_v.is_prerelease:
                result['bugfixpre'] = release
            else:
                result['bugfix'] = release
            continue

    # filter out older
    if (
        result['major'] and
        result['majorpre'] and
        parse_version(result['majorpre']) < parse_version(result['major'])
    ):
        result['majorpre'] = None
    if (
        result['minor'] and
        result['minorpre'] and
        parse_version(result['minorpre']) < parse_version(result['minor'])
    ):
        result['minorpre'] = None
    if (
        result['bugfix'] and
        result['bugfixpre'] and
        parse_version(result['bugfixpre']) < parse_version(result['bugfix'])
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
            pkgs[pkgname][current],
            session
        )
        if not state:
            sys.stderr.write('E')
            errors.append((pkgname, pkgs[pkgname][current], str(result)))
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
