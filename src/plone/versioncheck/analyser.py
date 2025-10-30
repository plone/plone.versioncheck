from collections import OrderedDict
from packaging.version import InvalidVersion
from packaging.version import parse as parse_version
from typing import Any


def uptodate_analysis(
    pkginfo: OrderedDict[str, dict[str, Any]], pypiinfo: dict[str, Any]
) -> list[str]:
    """analyse if used version is current:

    result:
        if empty then most recent
        if 'cfg' in result, some cfg is newer
        if 'pypifinal' in result, some pypi final release is newer
        if 'pypiprerelease' in result, some pypi prerelease is newer

    """
    result = []
    if is_cfg_newer(pkginfo):
        result.append("cfg")
    newer = is_pypi_newer(pypiinfo)
    if newer:
        result.append(newer)
    return result


def is_cfgidx_newer(pkginfo: dict[str, dict[str, Any]], target_idx: int) -> bool:
    """check if a given idx (>0) version is newer than the firstversion

    returns boolean
    """
    vcur = None
    for idx, key in enumerate(pkginfo):
        version = pkginfo[key]["v"]
        if not version:
            continue
        try:
            if idx == 0:
                vcur = parse_version(version)
            if idx == target_idx and vcur is not None:
                return parse_version(version) > vcur
        except (InvalidVersion, TypeError):
            # Skip invalid versions (e.g., ">= 1.1" or other non-PEP 440 versions)
            continue
    return False


def is_cfg_newer(pkginfo: dict[str, dict[str, Any]]) -> bool:
    """checks if one of the cfg is newer

    returns boolean
    """
    return any(is_cfgidx_newer(pkginfo, idx) for idx in range(1, len(pkginfo)))


TEST_FINALS = {"major", "minor", "bugfix"}
TEST_PRERELEASE = {"majorpre", "minorpre", "bugfixpre"}


def is_pypi_newer(pypiinfo: dict[str, Any]) -> str | bool:
    """Check if PyPI has newer versions"""
    keys = {_ for _ in pypiinfo if pypiinfo.get(_, False)}
    if TEST_FINALS.intersection(keys):
        return "pypifinal"
    if TEST_PRERELEASE.intersection(keys):
        return "pypiprerelease"
    return False
