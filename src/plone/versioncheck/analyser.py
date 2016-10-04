# -*- coding: utf-8 -*-
from pkg_resources import parse_version


def uptodate_analysis(pkginfo, pypiinfo):
    """analyse if used version is current:

    result:
        if empty then most recent
        if 'cfg' in result, some cfg is newer
        if 'pypifinal' in result, some pypi final release is newer
        if 'pypiprerelease' in result, some pypi prerelease is newer

    """
    result = []
    if is_cfg_newer(pkginfo):
        result.append('cfg')
    newer = is_pypi_newer(pypiinfo)
    if newer:
        result.append(newer)
    return result


def is_cfgidx_newer(pkginfo, target_idx):
    """check if a given idx (>0) version is newer than the firstversion

    returns boolean
    """
    vcur = None
    for idx, key in enumerate(pkginfo):
        version = pkginfo[key]['v']
        if not version:
            continue
        if idx == 0:
            vcur = parse_version(version)
        if idx == target_idx:
            return parse_version(version) > vcur
    return False


def is_cfg_newer(pkginfo):
    """ checks if one of the cfg is newer

    returns boolean
    """
    for idx in range(1, len(pkginfo)):
        if is_cfgidx_newer(pkginfo, idx):
            return True


TEST_FINALS = set(['major', 'minor', 'bugfix'])
TEST_PRERELEASE = set(['majorpre', 'minorpre', 'bugfixpre'])


def is_pypi_newer(pypiinfo):
    keys = {_ for _ in pypiinfo if pypiinfo.get(_, False)}
    if TEST_FINALS.intersection(keys):
        return 'pypifinal'
    if TEST_PRERELEASE.intersection(keys):
        return 'pypiprerelease'
    return False
