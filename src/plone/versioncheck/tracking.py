# inspired partly by dumppickedversions
from typing import Any, Callable

from zc.buildout import easy_install

from plone.versioncheck.utils import find_relative

# zc.buildout may vendorize its own copy of pkg_resources
# Define DEVELOP_DIST locally as recommended in issue #57
DEVELOP_DIST = "-1"

import json
import logging
import os
import sys
import time

logger = easy_install.logger

required_by: dict[str, list[str]] = {}
versions_by_name: dict[str, tuple[str, str | bool]] = {}

TRACKINGFILENAME = ".plone.versioncheck.tracked.json"


def track_get_dist(old_get_dist: Callable) -> Callable:
    """Wrap Installer._get_dist to track version usage"""

    def get_dist(self: Any, requirement: Any, *ags: Any, **kw: Any) -> Any:
        dists = old_get_dist(self, requirement, *ags, **kw)
        for dist in dists:
            dist_name = dist.project_name.lower()
            versions_by_name[dist_name] = (
                dist.version,
                (
                    dist.precedence == DEVELOP_DIST
                    and
                    # heuristics, may fail if not named site-packages
                    "site-packages" not in dist.location
                    and dist.location
                ),
            )
            if dist_name not in required_by:
                required_by[dist_name] = []
            if (
                requirement.key != dist_name
                and requirement.key not in required_by[dist_name]
            ):
                required_by[dist_name].append(requirement.key)
            for req in dist.requires():
                if req.key not in required_by:
                    required_by[req.key] = []
                if dist_name not in required_by[req.key]:
                    required_by[req.key].append(dist_name)
        return dists

    return get_dist


def write_tracked(old_logging_shutdown: Callable, logfilepath: str) -> Callable:
    """Wrap logging.shutdown to write tracking file"""

    def logging_shutdown() -> None:
        # WRITE FILE
        result = {
            "generated": time.time(),
            "required_by": required_by,
            "versions": versions_by_name,
        }
        with open(logfilepath, "w") as fp:
            json.dump(result, fp, indent=2)
        old_logging_shutdown()

    return logging_shutdown


def install(buildout: dict[str, Any]) -> None:
    """Install tracking extension into buildout"""
    filepath = os.path.join(buildout["buildout"]["directory"], TRACKINGFILENAME)
    easy_install.Installer.__tracked_versions = {}
    easy_install.Installer._get_dist = track_get_dist(easy_install.Installer._get_dist)
    logging.shutdown = write_tracked(logging.shutdown, filepath)


def get(pkginfo: dict[str, Any], buildout: str) -> None:
    """Read tracking information from file"""
    filepath = TRACKINGFILENAME
    relative, filename = find_relative(buildout)
    if relative:
        filepath = os.path.join(relative, TRACKINGFILENAME)
    if not os.path.exists(filepath):
        # We are not used as a buildout extension, so this file is
        # not available.
        return
    sys.stderr.write(
        "\nRead tracking information from buildout extension: \n"
        "- {0}\n".format(filepath)
    )
    try:
        with open(filepath, "r") as fp:
            pkginfo["tracking"] = json.load(fp)
    except (IOError, ValueError) as e:
        sys.stderr.write(" - " + str(e) + "\n")
        return
    delta = time.time() - pkginfo["tracking"]["generated"]
    days = int(delta // (60 * 60 * 24))
    hours = int(delta // (60 * 60) - days * 60 * 60)
    minutes = int(delta // (60) - days * 60 * 60 - hours * 60)
    seconds = delta % 60
    sys.stderr.write(
        "- age of gathered data: {0:d}d {1:d}h {2:d}m {3:2.3f}s\n".format(
            days, hours, minutes, seconds
        )
    )
