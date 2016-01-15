# -*- coding: utf-8 -*-
from collections import OrderedDict
from plone.versioncheck import analyser
from plone.versioncheck.utils import color_by_state
from plone.versioncheck.utils import color_dimmed
from plone.versioncheck.utils import color_init
from plone.versioncheck.utils import dots


def build_version(
    name,
    pkg,
    pypi,
    key,
    idx,
    flavor='versions',
):
    record = {}
    if flavor == 'versions':
        record['version'] = pkg[key] or "(unet)"
        record['description'] = key
        if idx == 0:
            record['state'] = 'A'
        elif analyser.is_cfgidx_newer(pkg, idx):
            record['state'] = 'In'
        else:
            record['state'] = 'I'
    else:  # pypi
        if 'pre' in key:
            record['state'] = 'P'
        else:
            record['state'] = 'U'
        record['version'] = pypi[key]
        record['description'] = key.capitalize()
    return record


def builder(pkgsinfo, newer_only=False, limit=None):
    """build
    - OrderedDict with pkgname as keys
    - each entry an record:
      - state: overall package state
      - versions: list of dicts with
        - version number
        - state
        - description
    """
    result = OrderedDict()
    pkgs = pkgsinfo['pkgs']
    pypi = pkgsinfo.get('pypi', {})
    used = pkgsinfo.get('tracking', {}).get('versions', {})
    requ = pkgsinfo.get('tracking', {}).get('required_by', {})
    for nidx, name in enumerate(sorted(pkgs)):
        if limit and limit == nidx:
            break
        current_pkg = pkgs[name]
        record = dict()
        versions = record['versions'] = list()
        record['required_by'] = requ

        # handle dev-eggs
        devegg = False
        if name in used and used[name][1]:
            versions.append({
                'version': used[name][0],
                'state': 'D',
                'description': used[name][1],
            })
            devegg = True

        # handle versions.cfg and inherited
        for idx, location in enumerate(current_pkg):
            versions.append(
                build_version(
                    name,
                    current_pkg,
                    pypi.get(name, {}),
                    location,
                    idx,
                    flavor='versions',
                )
            )
        if pypi.get(name, None) is not None:
            current_pypi = pypi[name]
            for label, version in current_pypi.items():
                if version is None:
                    continue
                versions.append(
                    build_version(
                        name,
                        current_pkg,
                        current_pypi,
                        label,
                        idx,
                        flavor='pypi',
                    )
                )

        states = analyser.uptodate_analysis(current_pkg, pypi.get(name, None))
        if devegg:
            # dev always wins
            record['state'] = 'D'
        elif 'pypifinal' in states:
            record['state'] = 'U'
        elif 'cfg' in states:
            record['state'] = 'In'
        elif 'pypifinal' in states:
            record['state'] = 'P'
        else:
            record['state'] = 'A'

        if newer_only and record['state'] == 'A':
            continue

        result[name] = record
    return result


def display(pkgsinfo, newer_only=False, colored=True, limit=None):
    color_init()
    print 'Result'
    print '------'
    data = builder(pkgsinfo, newer_only=newer_only, limit=limit)
    for name, record in data.items():
        print color_by_state(record['state']) + name
        for version in record['versions']:
            print \
                ' ' * 4 + \
                color_by_state(version['state']) + \
                version['version'] + ' ' + \
                dots(version['version'], pkgsinfo['ver_maxlen']-1) + \
                ' ' + color_by_state(version['state']) + \
                version['state'][0] + ' ' + version['description']
