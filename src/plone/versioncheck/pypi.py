# -*- coding: utf-8 -*-

from collections import namedtuple
from collections import OrderedDict
from pkg_resources import parse_version
from plone.versioncheck.utils import requests_session

import datetime
import sys


PYPI_URL = 'https://pypi.python.org/pypi'


Release = namedtuple('Release', ['version', 'release_date'])

FLOOR_RELEASE = Release(
    version=u'0.0.0.0',
    release_date=datetime.date(1970, 1, 1),
)


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
        ('major', FLOOR_RELEASE),
        ('minor', FLOOR_RELEASE),
        ('bugfix', FLOOR_RELEASE),
        ('majorpre', FLOOR_RELEASE),
        ('minorpre', FLOOR_RELEASE),
        ('bugfixpre', FLOOR_RELEASE),
    ])

    # parse version to test against:
    try:
        version = parse_version(version)
    except TypeError:
        return False, 'Version broken/ not checkable.'
    try:
        vtuple = mmbp_tuple(version)
    except ValueError:
        return False, 'Can not check legacy version number.'

    # fetch pkgs json info from pypi
    url = '{url}/{name}/json'.format(url=PYPI_URL, name=name)
    resp = session.get(url)

    # check status code
    if resp.status_code == 404:
        return False, 'Package "{name}" not on pypi.'.format(name=name)
    elif resp.status_code != 200:
        return False, str(resp.status_code)
    data = resp.json()

    # get information about possible updates
    releases = sorted(data['releases'])
    for release in releases:
        # major check (overall)
        rel_v = parse_version(release)
#        if not isinstance(rel_v, SetuptoolsVersion) or not rel_v > version:
        if rel_v <= version:
            continue
        rel_vtuple = mmbp_tuple(rel_v)
        rel_data = data['releases'][release]
        rel_date = datetime.date(1970, 1, 1)
        for rel_pkg in rel_data:
            time_string = rel_pkg.get('upload_time')
            if time_string:
                crel_date = datetime.datetime.strptime(
                    time_string, '%Y-%m-%dT%H:%M:%S').date()
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
            '\nError in {0} version {1} reason: {2}'.format(
                *error
            )
        )

    sys.stderr.write('\nPyPI check finished\n')


def update_pkg_info(pkg_name, pkg_data, session):
    for filename, elemdata in pkg_data.items():
        # fetch pkgs json info from pypi
        url = '{url}/{name}/json'.format(url=PYPI_URL, name=pkg_name)
        resp = session.get(url)

        # check status code
        if resp.status_code != 200:
            continue
        data = resp.json()

        rel_date = datetime.date(1970, 1, 1)
        try:
            urls = data['releases'][elemdata['v']]
        except KeyError:
            # release not on PyPI
            continue
        for rel_pkg in urls:
            time_string = rel_pkg.get('upload_time')
            if time_string:
                crel_date = datetime.datetime.strptime(
                    time_string, '%Y-%m-%dT%H:%M:%S').date()
                if crel_date > rel_date:
                    rel_date = crel_date
        elemdata['release_date'] = rel_date

    return True


def update_pkgs_info(pkgsinfo, limit=None, nocache=False):
    session = requests_session(nocache=nocache)
    pkgs = pkgsinfo['pkgs']
    sys.stderr.write(
        'Check PyPI for data of {0:d} packages.'.format(len(pkgs))
    )
    if limit:
        sys.stderr.write(' Check limited to {0:d} packages.'.format(limit))
    errors = []

    idx = 0
    for pkg_name, pkg_data in pkgs.items():
        if not idx % 20 and idx != limit:
            sys.stderr.write('\n{0:4d} '.format(idx))

        state = update_pkg_info(pkg_name, pkg_data, session)
        if not state:
            sys.stderr.write('E')
            errors.append((pkg_name, ))
            continue
        sys.stderr.write('O' if state == 1 else 'o')
        if limit and idx == limit:
            break
        idx += 1

    for error in errors:
        sys.stderr.write(
            '\nError in {0}'.format(
                *error
            )
        )

    sys.stderr.write('\nPyPI check finished\n')


def update_tracking_version_info(pkg_name, pkg_data, session):
    # fetch pkgs json info from pypi
    url = '{url}/{name}/{version}/json'.format(url=PYPI_URL,
                                               name=pkg_name,
                                               # version=pkg_data['version'])
                                               version=pkg_data[0])
    resp = session.get(url)

    # check status code
    if resp.status_code == 404:
        return False, 'Package Version not on pypi.'
    elif resp.status_code != 200:
        return False, str(resp.status_code)
    data = resp.json()

    rel_date = datetime.date(1970, 1, 1)
    for rel_pkg in data['urls']:
        time_string = rel_pkg.get('upload_time')
        if time_string:
            crel_date = datetime.datetime.strptime(
                time_string, '%Y-%m-%dT%H:%M:%S').date()
            if crel_date > rel_date:
                rel_date = crel_date
    # pkg_data['release_date'] = rel_date
    pkg_data.append(rel_date)

    return 2 if resp.from_cache else 1, True


def update_tracking_info(pkgsinfo, nocache=False):
    session = requests_session(nocache=nocache)
    pkgs = pkgsinfo['tracking']['versions']
    sys.stderr.write(
        'Check PyPI for data of {0:d} packages.'.format(len(pkgs))
    )
    errors = []

    idx = 0
    for pkg_name, pkg_data in pkgs.items():
        if not idx % 20:
            sys.stderr.write('\n{0:4d} '.format(idx))

        state, result = update_tracking_version_info(pkg_name,
                                                     pkg_data,
                                                     session)
        if not state:
            sys.stderr.write('E')
            errors.append((pkg_name, str(result)))
            continue
        sys.stderr.write('O' if state == 1 else 'o')
        idx += 1

    for error in errors:
        sys.stderr.write(
            '\nError in {0} reason: {1}'.format(
                *error
            )
        )

    sys.stderr.write('\nPyPI check finished\n')
