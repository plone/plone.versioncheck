# -*- coding: utf-8 -*-
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
from plone.versioncheck import analyser

# color codes:

# pkgname all bright
# ------------------
# white: no newer pypi, no newer cfgs
# green:  newer pypi finals, no newer cfgs
# blue: newer pypi prerelease only, no newer cfgs
# red:  newer in both, pypi final and cfgs
# cyan:  newer in both, pypi prerelease and cfgs
# yellow newer in cfgs

# all dots gray dimmed

# version / location (w/o dots)
# white current used
# dimmed white unused and older
# green pypi final newer
# blue pypi prerelease newer
# yellow cfgs newer


def dots(value, number):
    """ljust, but the dots only"""
    return '.' * (number - len(value))


def format_line(name,
                pkg, pypi,
                key, idx,
                ver_maxlen, pkg_maxlen,
                flavor='versions',
                colored=True):
    # prepare
    line = Style.RESET_ALL if colored else ''

    # before version
    if idx == 0:
        # format
        if colored:
            line += Style.BRIGHT
            state = analyser.uptodate_analysis(pkg, pypi)
            if 'cfg' in state and 'pypifinal' in state:
                line += Fore.RED
            elif 'cfg' in state and 'pypiprerelease' in state:
                line += Fore.CYAN
            elif 'cfg' in state:
                line += Fore.YELLOW
            elif 'pypifinal' in state:
                line += Fore.GREEN
            elif 'pypiprerelease' in state:
                line += Fore.BLUE
            else:
                line += Fore.WHITE
        line += name
        if colored:
            line += Style.DIM + Fore.WHITE
        line += dots(name, pkg_maxlen)
    else:
        line += ' ' * (pkg_maxlen)
    line += Style.RESET_ALL if colored else ''

    # versions
    color = ''
    displayname = key
    if flavor == 'versions':
        version = pkg[key]
        if colored:
            if idx == 0:
                color = Style.BRIGHT + Fore.WHITE
            elif analyser.is_cfgidx_newer(pkg, idx):
                color = Fore.YELLOW
            else:
                color = Style.DIM + Fore.WHITE
            pass
    else:
        if colored:
            # find a color
            color = Style.BRIGHT + Fore.BLUE
            pass
        displayname = key + ' (PyPI)'
        version = pypi[key]

    line += ' ' + color + version + dots(version, ver_maxlen)
    line += ' ' + color + displayname
    line += Style.RESET_ALL if colored else ''

    return line


def display(pkgsinfo, overrides_only=False, colored=True, limit=None):
    color = ''
    if colored:
        colorama_init()
        color += Style.BRIGHT
        color += Fore.CYAN
    print color + 'Check Versions'
    if colored:
        color = Style.DIM
    print color + '--------------'
    pkgs = pkgsinfo['pkgs']
    pypi = pkgsinfo.get('pypi', {})
    for nidx, name in enumerate(sorted(pkgs)):
        if limit and limit == nidx:
            break
        if overrides_only and len(pkgs[name]) < 2:
            continue
        current_pkg = pkgs[name]
        for idx, location in enumerate(current_pkg):
            print \
                format_line(
                    name,
                    current_pkg,
                    pypi.get(name, {}),
                    location,
                    idx,
                    pkgsinfo['ver_maxlen'],
                    pkgsinfo['pkg_maxlen'],
                    flavor='versions',
                    colored=colored
                )

        if pypi.get(name, None) is None:
            continue
        current_pypi = pypi[name]
        for label, version in current_pypi.items():
            if version is None:
                continue
            print \
                format_line(
                    name,
                    current_pkg,
                    current_pypi,
                    label,
                    -1,
                    pkgsinfo['ver_maxlen'],
                    pkgsinfo['pkg_maxlen'],
                    flavor='pypi',
                    colored=colored
                )
