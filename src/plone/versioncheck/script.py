# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from plone.versioncheck import formatter
from plone.versioncheck.parser import parse
from plone.versioncheck.pypi import check_all
from plone.versioncheck import tracking


parser = ArgumentParser(
    description="Fetch information about pinned versions and its overrides in"
                "simple and complex/cascaded buildouts."
)
parser.add_argument(
    'buildout',
    nargs='?',
    default='buildout.cfg',
    help='path to buildout.cfg or other *.cfg file'
)
parser.add_argument(
    "-p",
    "--pypi",
    help='check pypi for newer versions',
    action="store_true"
)
parser.add_argument(
    "-n",
    "--newer",
    help='display only packages with newer version than active',
    action="store_true"
)
parser.add_argument(
    "-r",
    "--required-by",
    help='show information about requirements (only if tracking file is '
         'available)',
    action="store_true"
)
parser.add_argument(
    "-i",
    "--ignore-tracking",
    help='ignore tracking file (if present)',
    action="store_true"
)
parser.add_argument(
    "-m",
    "--machine",
    help='show as machine readable output (json)',
    action="store_true"
)
parser.add_argument(
    '--no-colors',
    help='do not show colors',
    action="store_true"
)
parser.add_argument(
    '--debug-limit',
    type=int,
    help='Limit the number of pypi versions fetched for debugging'
)


def run():
    args = parser.parse_args()
    pkgsinfo = {}
    pkgsinfo['pkgs'] = parse(args.buildout)
    if args.pypi:
        check_all(pkgsinfo, args.debug_limit)
    if not args.ignore_tracking:
        tracking.get(pkgsinfo, args.buildout)
    if args.machine:
        formatter.machine(
            pkgsinfo,
            newer_only=args.newer,
            limit=args.debug_limit,
        )
    else:
        formatter.human(
            pkgsinfo,
            newer_only=args.newer,
            colored=args.no_colors,
            limit=args.debug_limit,
        )
