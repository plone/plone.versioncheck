# -*- coding: utf-8 -*-
from collections import OrderedDict
from pkg_resources import parse_version
from pkg_resources import SetuptoolsVersion
import logging
import requests

logger = logging.getLogger(__name__)


PYPI_URL = "https://pypi.python.org/pypi"


def check(name, version):
    result = OrderedDict([
        ('error', None),
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
        result['error'] = "Version not checkable (TypeError)."
        return result
    if not isinstance(version, SetuptoolsVersion):
        result['error'] = "Version not checkable (Legacy)."
        return result
    no_minor = len(tuple(version)) < 2 or version[1].startswith('*')
    no_bugfix = (
        no_minor or
        len(tuple(version)) < 3 or
        version[2].startswith('*')
    )

    # fetch pkgs json info from pypi
    url = "{0}/{1}/json".format(PYPI_URL, name)
    resp = requests.get(url)

    # TODO check status code
    if resp.status_code != 200:
        result['error'] = str(resp.status_code)
        return result
    data = resp.json()
    releases = sorted(data['releases'].keys())
    for release in releases:
        # major check (overall)
        rel_v = parse_version(release)
        if not isinstance(rel_v, SetuptoolsVersion) or not rel_v > version:
            continue
        if rel_v[0] > version[0]:
            if rel_v.is_prerelease:
                result['majorpre'] = release
            else:
                result['major'] = release
            continue
        if no_minor or len(tuple(rel_v)) < 2 or rel_v[1].startswith('*'):
            # version like '10'
            continue
        if rel_v[1] > version[1]:
            if rel_v.is_prerelease:
                result['minorpre'] = release
            else:
                result['minor'] = release
            continue
        if no_bugfix or len(tuple(rel_v)) < 3 or rel_v[2].startswith('*'):
            # version like '10.1'
            continue
        if rel_v[2] > version[2]:
            if rel_v.is_prerelease:
                result['bugfixpre'] = release
            else:
                result['bugfix'] = release
            continue

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

    return result


def check_all(pkgsinfo, limit=None):
    pkgsinfo['pypi'] = {}
    pkgs = pkgsinfo['pkgs']
    for idx, pkgname in enumerate(sorted(pkgs)):
        logger.info('{0} pypi check {1}'.format(idx+1, pkgname))
        current = next(iter(pkgs[pkgname]))
        pkgsinfo['pypi'][pkgname] = check(
            pkgname,
            pkgs[pkgname][current]
        )
        if limit and idx == limit:
            break
