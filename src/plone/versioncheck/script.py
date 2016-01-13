# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from plone.versioncheck.formatter import display
from plone.versioncheck.parser import parse
from plone.versioncheck.pypi import check_all

parser = ArgumentParser(
    description="Print info about pinned versions and its overrides"
)
parser.add_argument(
    "-b",
    "--buildout",
    help='path to buildout.cfg or other cfg file',
    default='buildout.cfg'
)
parser.add_argument(
    "-o",
    "--overrides",
    help='display only packages with overrides',
    action="store_true"
)
parser.add_argument(
    "-p",
    "--pypi",
    help='check pypi for newer versions',
    action="store_true"
)
parser.add_argument(
    '--debug-limit',
    type=int,
    help='Limit the number of pypi versions fetched for debugging'
)


def run():
    args = parser.parse_args()
    pkgsinfo = parse(args.buildout)
    if args.pypi:
        check_all(pkgsinfo, args.debug_limit)
    display(pkgsinfo, overrides_only=args.overrides, limit=args.debug_limit)
