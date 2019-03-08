# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from plone.versioncheck import formatter
from plone.versioncheck import tracking
from plone.versioncheck import utils
from plone.versioncheck.parser import parse
from plone.versioncheck.pypi import check_all
from plone.versioncheck.pypi import update_pkgs_info
from plone.versioncheck.pypi import update_tracking_info

import argparse
import sys


EPILOG = """\
States and color codes:
  [A]ctive (white)
  [D]evelop (green)
  [O]rphaned (magenta)
  [I]nherited (older or same versions are gray, newer are yellow)
  [U]pdate of final release on PyPI available (cyan)
  [P]rerelease update on PyPI available (blue)
  [X] unpinned (red)
  [r] Requirement (gray)
  [a] Annotation (gray)

Color of package name helps to indicate overall state of a package.
"""


parser = ArgumentParser(
    description="Fetch information about pinned versions and its overrides in "
    "simple and complex/cascaded buildouts.",
    epilog=EPILOG,
    formatter_class=RawDescriptionHelpFormatter,
)
parser.add_argument(
    "buildout",
    nargs="?",
    default="buildout.cfg",
    help="path to buildout.cfg or other *.cfg file",
)
parser.add_argument(
    "-p", "--pypi", help="check PyPI for newer versions", action="store_true"
)
parser.add_argument(
    "-n",
    "--newer",
    help="display only packages with newer version than active",
    action="store_true",
)
parser.add_argument(
    "-N",
    "--newer-orphaned",
    help="display orphaned packages only when newer versions available",
    action="store_true",
)
parser.add_argument(
    "-r",
    "--required-by",
    help="show information about requirements (only if tracking file is " "available)",
    default=False,
    action="store_true",
)
parser.add_argument(
    "-d",
    "--show-release-dates",
    help="show information about release dates " "(only for package lookup from PyPI)",
    default=False,
    action="store_true",
    dest="show_release_dates",
)
parser.add_argument(
    "-i",
    "--ignore-tracking",
    help="ignore tracking file (if present)",
    action="store_true",
)
parser.add_argument(
    "-e",
    "--exclude-cfg",
    help=(
        "exclude in listing when cfg-filename pattern matches (fnmatch) the "
        "given expression"
    ),
    action="append",
)
parser.add_argument(
    "-m",
    "--machine",
    help="show as machine readable output (json)",
    action="store_true",
)
parser.add_argument(
    "--no-cache", help="do not use a cache for PyPI", action="store_true"
)
parser.add_argument(
    "-b", "--browser", help="show as html for webbrowser", action="store_true"
)
parser.add_argument(
    "-o",
    "--output",
    help="safe output to output-file",
    nargs="?",
    type=argparse.FileType("w"),
    default=sys.stdout,
)
parser.add_argument("--no-colors", help="do not show colors", action="store_true")
parser.add_argument(
    "--debug-limit",
    type=int,
    help="Limit the number of PyPI versions fetched for debugging",
)


def run():
    args = parser.parse_args()
    pkgsinfo = {}
    pkgsinfo["pkgs"] = parse(args.buildout)

    # retrieve additional informations
    if not args.ignore_tracking:
        tracking.get(pkgsinfo, args.buildout)
    if args.pypi:
        check_all(pkgsinfo, args.debug_limit, nocache=args.no_cache)
        if args.show_release_dates:
            update_pkgs_info(pkgsinfo, args.debug_limit, nocache=args.no_cache)
            if not args.ignore_tracking:
                update_tracking_info(pkgsinfo, nocache=args.no_cache)

    # Create output
    if args.machine:
        formatter.machine(
            pkgsinfo,
            newer_only=args.newer,
            newer_orphaned_only=args.newer_orphaned,
            limit=args.debug_limit,
            exclude_cfgs=args.exclude_cfg,
            file=args.output,
        )
    elif args.browser:
        formatter.browser(
            pkgsinfo,
            newer_only=args.newer,
            newer_orphaned_only=args.newer_orphaned,
            limit=args.debug_limit,
            exclude_cfgs=args.exclude_cfg,
            show_requiredby=args.required_by,
            show_release_dates=args.show_release_dates,
            file=args.output,
        )
    else:
        utils.COLORED = not args.no_colors
        formatter.human(
            pkgsinfo,
            newer_only=args.newer,
            newer_orphaned_only=args.newer_orphaned,
            limit=args.debug_limit,
            exclude_cfgs=args.exclude_cfg,
            show_requiredby=args.required_by,
        )
