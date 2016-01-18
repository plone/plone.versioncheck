# -*- coding: utf-8 -*-
# inspired partly by dumppickedversions
from pkg_resources import DEVELOP_DIST
from plone.versioncheck.utils import find_relative
from zc.buildout import easy_install
import json
import logging
import os

logger = easy_install.logger

required_by = {}
versions_by_name = {}

TRACKINGFILENAME = '.plone.versioncheck.tracked.json'


def _log_requirement(ws, req):
    for dist in sorted(list(ws)):
        if req not in dist.requires():
            continue
        req_ = str(req)
        dist_ = str(dist)
        if req_ in required_by and dist_ not in required_by[req_]:
            required_by[req_].append(dist_)
        else:
            required_by[req_] = [dist_]


def enable_tracking(old_get_dist):
    def get_dist(self, requirement, *ags, **kw):
        dists = old_get_dist(self, requirement, *ags, **kw)
        for dist in dists:
            if not (
                len(requirement.specs) == 1 and  # ???
                requirement.specs[0][0] == '=='  # ???
            ):
                versions_by_name[dist.project_name] = (
                    dist.version,
                    dist.precedence == DEVELOP_DIST and dist.location
                )
        return dists
    return get_dist


def write_tracked(old_logging_shutdown, logfilepath):

    def logging_shutdown():
        # WRITE FILE
        result = {
            'required_by': required_by,
            'versions': versions_by_name,
        }
        with open(logfilepath, 'a') as fp:
            json.dump(result, fp, indent=2)
        old_logging_shutdown()
    return logging_shutdown


def install(buildout):
    filepath = os.path.join(
        buildout['buildout']['directory'],
        TRACKINGFILENAME,
    )
    easy_install.Installer.__tracked_versions = {}
    easy_install._log_requirement = _log_requirement
    easy_install.Installer._get_dist = enable_tracking(
        easy_install.Installer._get_dist
    )
    logging.shutdown = write_tracked(logging.shutdown, filepath)


def get(pkginfo, buildout):
    relative = find_relative(buildout)
    filepath = os.path.join(relative, TRACKINGFILENAME)
    with open(filepath, 'r') as fp:
        pkginfo['tracking'] = json.load(fp)