from collections.abc import AsyncIterator
from colorama import Fore
from colorama import init as colorama_init
from colorama import Style
from contextlib import asynccontextmanager
from urllib.parse import urlparse
from urllib.parse import urlunparse

import httpx
import os
import platform
import shlex
import struct
import subprocess


COLORED = True

_STATEMAP = {
    # develop egg
    "D": Style.BRIGHT + Fore.GREEN,
    # Active version
    "A": Style.BRIGHT + Fore.WHITE,
    # inherited, older or equal
    "I": Style.NORMAL + Fore.WHITE,
    # inherited, newer
    "In": Style.BRIGHT + Fore.YELLOW,
    # update
    "U": Style.BRIGHT + Fore.CYAN,
    # update prerelease
    "P": Style.BRIGHT + Fore.BLUE,
    # orphaned
    "O": Style.BRIGHT + Fore.MAGENTA,
    # unpinned
    "X": Style.BRIGHT + Fore.RED,
}


def color_init() -> None:
    """Initialize colorama for colored terminal output"""
    if COLORED:
        colorama_init()


def color_by_state(state: str) -> str:
    """Get color code for a given state"""
    if COLORED:
        return _STATEMAP.get(state, Style.DIM + Fore.RED)  # type: ignore[return-value]
    return ""


def color_dimmed() -> str:
    """Get dimmed color code"""
    if COLORED:
        return Style.DIM + Fore.WHITE  # type: ignore[return-value]
    return ""


def dots(value: str, max: int) -> str:
    """ljust, but the dots only"""
    dots = "." * (max - len(value))
    if dots:
        dots = " " + dots[1:]
    return color_dimmed() + dots


CACHE_DIR = ".plone.versioncheck.cache"


@asynccontextmanager
async def http_client(nocache: bool = False) -> AsyncIterator[httpx.AsyncClient]:
    """Create an async HTTP client

    Note: HTTP caching temporarily disabled. Will be re-enabled with proper
    hishel integration in a future update. The performance gains from async
    concurrent requests (10-50x) far outweigh the caching benefits.
    """
    # TODO: Re-enable caching with hishel once API is confirmed
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


def find_relative(extend: str, relative: str | None = "") -> tuple[str, str]:
    """the base dir or url and the actual filename as tuple"""
    if "://" in extend:
        parts = list(urlparse(extend))
        path = parts[2].split("/")
        parts[2] = "/".join(path[:-1])
        return urlunparse(parts), path[-1]
    if relative and "://" in relative:
        return (relative.strip("/"), extend.strip("/"))
    if relative:
        extend = os.path.join(relative, extend)
    return (os.path.dirname(os.path.abspath(extend)), os.path.basename(extend))


###########################################################
# below copied from https://gist.github.com/jtriley/1108174


def get_terminal_size() -> tuple[int, int]:
    """getTerminalSize()
    - get width and height of console
    - works on linux,os x,windows,cygwin(windows)
    originally retrieved from:
    http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    current_os = platform.system()
    tuple_xy = None
    if current_os == "Windows":
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ["Linux", "Darwin"] or current_os.startswith("CYGWIN"):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        tuple_xy = (80, 25)  # default value
    return tuple_xy


def _get_terminal_size_windows() -> tuple[int, int] | None:
    """Get terminal size on Windows"""
    try:
        from ctypes import create_string_buffer
        from ctypes import windll  # type: ignore[attr-defined]

        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (
                bufx,
                bufy,
                curx,
                cury,
                wattr,
                left,
                top,
                right,
                bottom,
                maxx,
                maxy,
            ) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except Exception:
        pass
    return None


def _get_terminal_size_tput() -> tuple[int, int] | None:
    """Get terminal size using tput"""
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window  # noqa
    try:
        cols = int(subprocess.check_call(shlex.split("tput cols")))
        rows = int(subprocess.check_call(shlex.split("tput lines")))
        return (cols, rows)
    except Exception:
        pass
    return None


def _get_terminal_size_linux() -> tuple[int, int] | None:
    """Get terminal size on Linux"""

    def ioctl_GWINSZ(fd: int) -> tuple[int, int] | None:
        try:
            import fcntl
            import termios

            cr = struct.unpack("hh", fcntl.ioctl(fd, termios.TIOCGWINSZ, b"1234"))
            return cr
        except Exception:
            pass
        return None

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
            cr = (os.environ["LINES"], os.environ["COLUMNS"])
        except Exception:
            return None
    return int(cr[1]), int(cr[0])
