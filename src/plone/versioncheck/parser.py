# -*- coding: utf-8 -*-
from collections import OrderedDict
from ConfigParser import ConfigParser
from ConfigParser import NoOptionError
from ConfigParser import NoSectionError
from plone.versioncheck.utils import find_relative
import os.path
import sys
import urllib2


def _extract_versions_section(filename, version_sections=None, relative=None):
    sys.stderr.write('\n- {0}'.format(filename))
    if (
        relative is not None and
        "://" not in filename and
        not filename.startswith('/') and
        not filename.startswith(relative)
    ):
        filename = relative + '/' + filename
    config = ConfigParser()
    if os.path.isfile(filename):
        config.read(filename)
    else:
        response = urllib2.urlopen(filename)
        config.readfp(response)
    # first read own versions section
    if config.has_section('versions'):
        version_sections[filename] = OrderedDict(config.items('versions'))
        sys.stderr.write(
            '\n  {0:d} entries in versions section.'.format(
                len(version_sections[filename])
            )
        )
    try:
        extends = config.get('buildout', 'extends').strip()
    except (NoSectionError, NoOptionError):
        return version_sections
    for extend in extends.splitlines():
        extend = extend.strip()
        if not extend:
            continue
        sub_relative = find_relative(extend) or relative
        _extract_versions_section(extend, version_sections, sub_relative)
    return version_sections


def parse(buildout_filename):
    sys.stderr.write("Parsing buildout files:")
    base_relative = find_relative(buildout_filename)
    version_sections = _extract_versions_section(
        buildout_filename,
        version_sections=OrderedDict(),
        relative=base_relative
    )
    sys.stderr.write("\nparsing finished.\n")
    pkgs = {}

    for name in version_sections:
        for pkg in version_sections[name]:
            if pkg not in pkgs:
                pkgs[pkg] = OrderedDict()

    for pkgname in pkgs:
        pkg = pkgs[pkgname]
        for name in version_sections:
            if pkgname in version_sections[name]:
                pkg[name] = version_sections[name][pkgname]

    return pkgs
