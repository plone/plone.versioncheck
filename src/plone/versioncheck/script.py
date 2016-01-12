# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from plone.versioncheck.formatter import display
from plone.versioncheck.parser import parse

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


def run():
    args = parser.parse_args()
    pkgsinfo = parse(args.buildout)
    display(pkgsinfo, overrides_only=args.overrides)

