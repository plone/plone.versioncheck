# -*- coding: utf-8 -*-
from collections import OrderedDict
from ConfigParser import ConfigParser
from ConfigParser import NoOptionError
from ConfigParser import NoSectionError
import logging
import os.path
import urllib2
import urlparse

logger = logging.getLogger(__name__)


def _find_relative(extend):
    if "://" in extend:
        parts = list(urlparse.urlparse(extend))
        parts[2] = '/'.join(parts[2].split('/')[:-1])
        return urlparse.urlunparse(parts)
    elif '/' in extend:
        return os.path.dirname(extend)


def _extract_versions_section(filename, version_sections=None, relative=None):
    if (
        relative is not None and
        "://" not in filename and
        not filename.startswith('/') and
        not filename.startswith(relative)
    ):
        filename = relative + '/' + filename
    logger.info('lookup versions in {0}'.format(filename))
    config = ConfigParser()
    if os.path.isfile(filename):
        config.read(filename)
    else:
        response = urllib2.urlopen(filename)
        config.readfp(response)
    if version_sections is None:
        version_sections = OrderedDict()
    # first read own versions section
    if config.has_section('versions'):
        version_sections[filename] = OrderedDict(config.items('versions'))
    try:
        extends = config.get('buildout', 'extends').strip()
    except (NoSectionError, NoOptionError):
        return {}
    for extend in extends.splitlines():
        extend = extend.strip()
        if not extend:
            continue
        sub_relative = _find_relative(extend) or relative
        _extract_versions_section(extend, version_sections, sub_relative)
    return version_sections


def parse(buildout_filename):
    base_relative = _find_relative(buildout_filename)
    version_sections = _extract_versions_section(
        buildout_filename,
        relative=base_relative
    )

    pkgs = {}
    pkg_maxlen = 0
    ver_maxlen = 0

    for name in version_sections:
        for pkg in version_sections[name]:
            if pkg not in pkgs:
                pkgs[pkg] = OrderedDict()

    for pkg in pkgs:
        pkg_maxlen = len(pkg) if len(pkg) > pkg_maxlen else pkg_maxlen
        for name in version_sections:
            if pkg in version_sections[name]:
                ver = version_sections[name][pkg]
                pkgs[pkg][name] = ver
                ver_maxlen = len(ver) if len(ver) > ver_maxlen else ver_maxlen

    return {
        'pkgs': pkgs,
        'pkg_maxlen': pkg_maxlen,
        'ver_maxlen': ver_maxlen,
    }
