# -*- coding: utf-8 -*-

from collections import OrderedDict
from plone.versioncheck.utils import find_relative
from plone.versioncheck.utils import requests_session
from zc.buildout import UserError
from zc.buildout.buildout import Buildout

import contextlib
import os.path
import sys


if sys.version_info < (3, 0):
    from ConfigParser import ConfigParser
    from ConfigParser import NoOptionError
    from ConfigParser import NoSectionError
    from StringIO import StringIO
elif sys.version_info >= (3, 0):
    from configparser import ConfigParser
    from configparser import NoOptionError
    from configparser import NoSectionError
    from io import StringIO


@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = StringIO()
    yield
    sys.stdout = save_stdout


def _extract_versions_section(  # NOQA: C901
    session,
    filename,
    base_dir=None,
    version_sections=None,
    annotations=None,
    relative=None,
    version_section_name=None,
    versionannotation_section_name='versionannotations'
):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(filename))
    if version_sections is None:
        version_sections = OrderedDict()
    if annotations is None:
        annotations = OrderedDict()
    if '://' not in filename:
        if relative and '://' in relative:
            # relative to url!
            filename = '{0}/{1}'.format(relative, filename)
        else:
            if relative:
                if filename.startswith(relative + '/'):
                    filename = filename[len(relative + '/'):]
                filename = os.path.join(base_dir, relative, filename)
            else:
                filename = os.path.join(base_dir, filename)

    sys.stderr.write('\n- {0}'.format(filename))

    try:
        with nostdout():
            buildout = Buildout(filename, [])  # Use zc.buildout parser
    except UserError:
        buildout = {'buildout': {}}
    config = ConfigParser()
    if os.path.isfile(filename):
        config.read(filename)
    else:
        resp = session.get(filename)
        config.readfp(StringIO(resp.text))
        if resp.from_cache:
            sys.stderr.write('\n  from cache')
        elif resp.status_code != 200:
            sys.stderr.write('\n  ERROR {0:d}'.format(resp.status_code))
        else:
            sys.stderr.write('\n  fresh from server')

    # first read own versions section
    current_version_section_name = buildout['buildout'].get(
        'versions',
        'versions',
    )
    if version_section_name is None:
        # initial name
        version_section_name = current_version_section_name
    elif version_section_name != current_version_section_name:
        # name changed, not sure if this works as expected! - jensens
        sys.stderr.write(
            '\nName of [versions] (versions = versions) has changed.'
            '\nGlobal versions section name: "{gname}"'
            '\nVersions pinned under that new Section namespace "{nname}"'
            ' will be ignored.'.format(
                gname=version_section_name,
                nname=buildout['buildout'].get('versions')))

    if filename.startswith(base_dir):
        key_name = filename[len(base_dir) + 1:]
    else:
        key_name = filename

    if config.has_section(version_section_name):
        version_sections[key_name] = OrderedDict(
            config.items(version_section_name)
        )
        sys.stderr.write(
            '\n  {0:d} entries in versions section.'.format(
                len(version_sections[key_name])
            )
        )

    # read versionannotations
    versionannotation_section_name = buildout['buildout'].get(
        'versionannotations', versionannotation_section_name)
    if config.has_section(versionannotation_section_name):
        annotations[key_name] = OrderedDict(
            config.items(versionannotation_section_name)
        )
        sys.stderr.write(
            '\n  {0:d} entries in annotations section.'.format(
                len(annotations[key_name])
            )
        )
    try:
        extends = config.get('buildout', 'extends').strip()
    except (NoSectionError, NoOptionError):
        return version_sections
    for extend in reversed(extends.splitlines()):
        extend = extend.strip()
        if not extend:
            continue
        sub_relative = find_relative(extend) or relative
        _extract_versions_section(
            session,
            extend,
            base_dir,
            version_sections,
            annotations,
            sub_relative,
            version_section_name,
            versionannotation_section_name
        )
    return version_sections, annotations


def parse(buildout_filename, nocache=False):
    sys.stderr.write('Parsing buildout files:')
    if nocache:
        sys.stderr.write('\n(not using caches)')
    base_relative = find_relative(buildout_filename)
    session = requests_session(nocache=nocache)
    version_sections, annotations = _extract_versions_section(
        session,
        buildout_filename,
        relative=base_relative
    )
    sys.stderr.write('\nparsing finished.\n')
    pkgs = {}

    for name in version_sections:
        for pkg in version_sections[name]:
            if pkg not in pkgs:
                pkgs[pkg] = OrderedDict()

    for pkgname in pkgs:
        pkg = pkgs[pkgname]
        for name in version_sections.keys():
            if pkgname in version_sections.get(name, {}):
                pkg[name] = {'v': version_sections[name][pkgname], 'a': ''}

        for name in annotations.keys():
            if pkgname in annotations.get(name, {}):
                if name in pkg:
                    pkg[name]['a'] = annotations[name][pkgname]
                else:
                    pkg[name] = {'v': None, 'a': annotations[name][pkgname]}

    return pkgs
