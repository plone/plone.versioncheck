# -*- coding: utf-8 -*-
from cachecontrol import CacheControl
from cachecontrol.caches import FileCache
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

import os
import platform
import requests
import shlex
import struct
import subprocess
import sys


if sys.version_info < (3, 0):
    from urlparse import urlparse
    from urlparse import urlunparse
elif sys.version_info >= (3, 0):
    from urllib.parse import urlparse
    from urllib.parse import urlunparse


COLORED = True

_STATEMAP = {
    # develop egg
    'D': Style.BRIGHT + Fore.GREEN,

    # Active version
    'A': Style.BRIGHT + Fore.WHITE,

    # inherited, older or equal
    'I': Style.NORMAL + Fore.WHITE,

    # inherited, newer
    'In': Style.BRIGHT + Fore.YELLOW,

    # update
    'U': Style.BRIGHT + Fore.CYAN,

    # update prerelease
    'P': Style.BRIGHT + Fore.BLUE,

    # orphaned
    'O': Style.BRIGHT + Fore.MAGENTA,

    # unpinned
    'X': Style.BRIGHT + Fore.RED,
}


def color_init():
    if COLORED:
        colorama_init()


def color_by_state(state):
    if COLORED:
        return _STATEMAP.get(state, Style.DIM + Fore.RED)
    return ''


def color_dimmed():
    if COLORED:
        return Style.DIM + Fore.WHITE
    return ''


def dots(value, max):
    """ljust, but the dots only"""
    dots = '.' * (max - len(value))
    if dots:
        dots = ' ' + dots[1:]
    return color_dimmed() + dots


CACHE_FILENAME = '.plone.versioncheck.cache'


def requests_session(nocache=False):
    if nocache:
        return requests.Session()
    return CacheControl(
        requests.Session(),
        cache=FileCache(CACHE_FILENAME)
    )


def find_relative(extend):
    if '://' in extend:
        parts = list(urlparse(extend))
        parts[2] = '/'.join(parts[2].split('/')[:-1])
        return urlunparse(parts)
    elif '/' in extend:
        return os.path.dirname(extend)

###########################################################
# below copied from https://gist.github.com/jtriley/1108174


def get_terminal_size():
    """ getTerminalSize()
     - get width and height of console
     - works on linux,os x,windows,cygwin(windows)
     originally retrieved from:
     http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        tuple_xy = (80, 25)      # default value
    return tuple_xy


def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack('hhhhHhhhhhh', csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except Exception:
        pass


def _get_terminal_size_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window  # noqa
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return (cols, rows)
    except Exception:
        pass


def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except Exception:
            pass
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except Exception:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except Exception:
            return None
    return int(cr[1]), int(cr[0])
