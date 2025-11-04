# inspired partly by dumppickedversions
from collections.abc import Callable
from plone.versioncheck.utils import find_relative
from typing import Any
from zc.buildout import easy_install

import json
import logging
import os
import sys
import time


# zc.buildout may vendorize its own copy of pkg_resources
# Define DEVELOP_DIST locally as recommended in issue #57
DEVELOP_DIST = -1


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
    easy_install.Installer.__tracked_versions = {}  # type: ignore[attr-defined]
    easy_install.Installer._get_dist = track_get_dist(easy_install.Installer._get_dist)  # type: ignore[method-assign, attr-defined]
    logging.shutdown = write_tracked(logging.shutdown, filepath)  # type: ignore[method-assign]


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
        f"\nRead tracking information from buildout extension: \n- {filepath}\n"
    )
    try:
        with open(filepath) as fp:
            pkginfo["tracking"] = json.load(fp)
    except (OSError, ValueError) as e:
        sys.stderr.write(" - " + str(e) + "\n")
        return
    delta = time.time() - pkginfo["tracking"]["generated"]
    days = int(delta // (60 * 60 * 24))
    hours = int(delta // (60 * 60) - days * 60 * 60)
    minutes = int(delta // (60) - days * 60 * 60 - hours * 60)
    seconds = delta % 60
    sys.stderr.write(
        f"- age of gathered data: {days:d}d {hours:d}h {minutes:d}m {seconds:2.3f}s\n"
    )
