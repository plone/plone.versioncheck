# -*- coding: utf-8 -*-
from colorama import Fore
from colorama import init as colorama_init
from colorama import Style
import os
import urlparse

COLORED = True

_STATEMAP = {
    # develop egg
    'D': Style.BRIGHT+Fore.GREEN,

    # Active version
    'A': Style.BRIGHT+Fore.WHITE,

    # inherited, older or equal
    'I': Style.NORMAL+Fore.WHITE,

    # inherited, newer
    'In': Style.BRIGHT+Fore.YELLOW,

    # update
    'U': Style.BRIGHT+Fore.CYAN,

    # update prerelease
    'P': Style.BRIGHT+Fore.BLUE,

    # orphaned
    'O': Style.BRIGHT+Fore.RED,
}


def color_init():
    if COLORED:
        colorama_init()


def color_by_state(state):
    if COLORED:
        return _STATEMAP.get(state, Style.DIM+Fore.RED)
    return ''


def color_dimmed():
    if COLORED:
        return Style.DIM + Fore.WHITE
    return ''


def dots(value, max):
    """ljust, but the dots only"""
    return color_dimmed() + '.' * (max - len(value))


def find_relative(extend):
    if "://" in extend:
        parts = list(urlparse.urlparse(extend))
        parts[2] = '/'.join(parts[2].split('/')[:-1])
        return urlparse.urlunparse(parts)
    elif '/' in extend:
        return os.path.dirname(extend)
