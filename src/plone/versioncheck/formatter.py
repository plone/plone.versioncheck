# -*- coding: utf-8 -*-
from __future__ import print_function
from collections import OrderedDict
from jinja2 import Environment
from jinja2 import PackageLoader
from plone.versioncheck import analyser
from plone.versioncheck.utils import color_by_state
from plone.versioncheck.utils import color_dimmed
from plone.versioncheck.utils import color_init
from plone.versioncheck.utils import dots
from plone.versioncheck.utils import get_terminal_size

import json
import sys
import textwrap


jenv = Environment(loader=PackageLoader('plone.versioncheck', 'tpl'))


def build_version(
    name,
    pkg,
    pypi,
    tracked,
    key,
    idx,
    flavor='versions',
    orphaned=False,
):
    record = {}
    if flavor == 'versions':
        record['description'] = key
        record['annotation'] = pkg[key]['a'].strip()
        if pkg[key]['v'] is None:
            record['version'] = '(annotation)'
            record['state'] = ''
            return record
        else:
            record['version'] = pkg[key]['v'] or '(unset)'
        if idx == 0:
            if orphaned:
                record['state'] = 'O'
            elif tracked and tracked[1]:
                record['state'] = 'I'
            else:
                record['state'] = 'A'
        elif analyser.is_cfgidx_newer(pkg, idx):
            record['state'] = 'In'
        else:
            record['state'] = 'I'
    else:  # pypi
        record['version'] = pypi[key]
        record['description'] = key.capitalize()
        record['annotation'] = None
        if 'pre' in key:
            record['state'] = 'P'
        else:
            record['state'] = 'U'
    return record


def builder(pkgsinfo, newer_only=False, newer_orphaned_only=False, limit=None):  # noqa: C901
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
    ver_maxlen = 0
    pkgs = pkgsinfo['pkgs']
    pypi = pkgsinfo.get('pypi', {})
    tracked = pkgsinfo.get('tracking', {}).get('versions', {})
    requ = pkgsinfo.get('tracking', {}).get('required_by', {})

    names = sorted(set(tracked.keys()) | set(pkgs.keys()))

    for nidx, name in enumerate(names):
        current_pkg = pkgs.get(name, {})
        record = dict()
        versions = record['versions'] = list()
        unpinned = False
        required_by = requ.get(name, None)
        if required_by:
            record['required_by'] = required_by

        # handle dev-eggs
        devegg = False
        current_tracked = tracked.get(name, None)
        if current_tracked is not None:
            ver_maxlen = max([ver_maxlen, len(current_tracked[0])])
            if current_tracked[1]:
                versions.append({
                    'version': current_tracked[0],
                    'state': 'D',
                    'description': current_tracked[1],
                })
                devegg = True

        # handle versions.cfg and inherited
        for idx, location in enumerate(current_pkg):
            ver_maxlen = max([ver_maxlen, len(current_pkg[location])])
            versions.append(
                build_version(
                    name,
                    current_pkg,
                    pypi.get(name, {}),
                    current_tracked,
                    location,
                    idx,
                    flavor='versions',
                    orphaned=tracked and current_tracked is None and not devegg
                )
            )
        if not devegg and current_tracked is not None and not len(versions):
            ver_maxlen = max([ver_maxlen, len(current_tracked[0])])
            versions.append({
                'version': current_tracked[0],
                'state': 'X',
                'description': 'unpinned',
            })
            unpinned = True

        if pypi.get(name, None) is not None:
            current_pypi = pypi[name]
            for label, version in current_pypi.items():
                if version is None:
                    continue
                ver_maxlen = max([ver_maxlen, len(version)])
                versions.append(
                    build_version(
                        name,
                        current_pkg,
                        current_pypi,
                        current_tracked,
                        label,
                        idx,
                        flavor='pypi',
                    )
                )

        pkgsinfo['ver_maxlen'] = ver_maxlen
        states = analyser.uptodate_analysis(
            current_pkg,
            pypi.get(name, {}),
        )
        if devegg:
            # dev always wins - not true!
            record['state'] = 'D'
        elif unpinned:
            record['state'] = 'X'
        elif tracked and name in pkgs and name not in tracked:
            record['state'] = 'O'
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
        if (
            newer_orphaned_only and
            record['versions'][0]['state'] == 'O' and
            len(record['versions']) == 1
        ):
            continue

        result[name] = record
    return result


def human(
    pkgsinfo,
    newer_only=False,
    newer_orphaned_only=False,
    limit=None,
    show_requiredby=False
):
    color_init()
    sys.stderr.write('\nReport for humans\n\n')
    data = builder(
        pkgsinfo,
        newer_only=newer_only,
        newer_orphaned_only=newer_orphaned_only,
        limit=limit
    )
    termx, termy = get_terminal_size()
    for name, record in data.items():
        print(color_by_state(record['state']) + name)
        for version in record['versions']:
            print(
                ' ' * 4 +
                color_by_state(version['state']) +
                version['version'] +
                dots(version['version'], pkgsinfo['ver_maxlen']) +
                ' ' + color_by_state(version['state']) +
                version['state'][0] + ' ' + version['description']
            )
            if version.get('annotation', None):
                indent = (pkgsinfo['ver_maxlen'] + 5) * ' ' + 'a '
                print(
                    color_dimmed() +
                    textwrap.fill(
                        version['annotation'],
                        termx - pkgsinfo['ver_maxlen'],
                        initial_indent=indent,
                        subsequent_indent=indent,
                    )
                )

        if show_requiredby and record.get('required_by', False):
            req = ' '.join(sorted(record.get('required_by')))
            indent = (pkgsinfo['ver_maxlen'] + 5) * ' ' + 'r '
            print(
                color_dimmed() +
                textwrap.fill(
                    req,
                    termx - pkgsinfo['ver_maxlen'],
                    initial_indent=indent,
                    subsequent_indent=indent,
                )
            )


def browser(
    pkgsinfo,
    newer_only=False,
    newer_orphaned_only=False,
    limit=None,
    show_requiredby=False
):
    color_init()
    sys.stderr.write('\nReport for brower\n\n')
    data = builder(
        pkgsinfo,
        newer_only=newer_only,
        newer_orphaned_only=newer_orphaned_only,
        limit=limit
    )
    template = jenv.get_template('browser.jinja')
    print(template.render(data=data, req_by=show_requiredby))


def machine(
    pkgsinfo,
    newer_only=False,
    newer_orphaned_only=False,
    limit=None
):
    sys.stderr.write('\nReport for machines\n\n')
    data = builder(
        pkgsinfo,
        newer_only=newer_only,
        newer_orphaned_only=newer_orphaned_only,
        limit=limit
    )
    print(json.dumps(data, indent=4))
