from collections import OrderedDict
from collections.abc import Iterator
from configparser import ConfigParser
from configparser import NoOptionError
from configparser import NoSectionError
from io import StringIO
from plone.versioncheck.utils import find_relative
from plone.versioncheck.utils import http_client
from typing import Any
from zc.buildout import UserError
from zc.buildout.buildout import Buildout

import contextlib
import httpx
import os.path
import sys


@contextlib.contextmanager
def nostdout() -> Iterator[None]:
    """Context manager to suppress stdout"""
    save_stdout = sys.stdout
    sys.stdout = StringIO()
    yield
    sys.stdout = save_stdout


async def _extract_versions_section(  # NOQA: C901
    client: httpx.AsyncClient,
    filename: str,
    base_dir: str | None = None,
    version_sections: OrderedDict[str, OrderedDict[str, str]] | None = None,
    annotations: OrderedDict[str, OrderedDict[str, str]] | None = None,
    relative: str | None = None,
    version_section_name: str | None = None,
    versionannotation_section_name: str = "versionannotations",
) -> tuple[
    OrderedDict[str, OrderedDict[str, str]], OrderedDict[str, OrderedDict[str, str]]
]:
    """Extract versions section from buildout file recursively"""
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(filename))
    if version_sections is None:
        version_sections = OrderedDict()
    if annotations is None:
        annotations = OrderedDict()
    if "://" not in filename:
        if relative and "://" in relative:
            # relative to url!
            filename = f"{relative}/{filename}"
        else:
            if relative:
                if filename.startswith(relative + "/"):
                    filename = filename[len(relative + "/") :]
                filename = os.path.join(base_dir, relative, filename)
            else:
                filename = os.path.join(base_dir, filename)

    sys.stderr.write(f"\n- {filename}")

    try:
        with nostdout():
            buildout = Buildout(filename, [])  # Use zc.buildout parser
    except UserError:
        buildout = {"buildout": {}}
    config = ConfigParser()
    if os.path.isfile(filename):
        config.read(filename)
    elif "://" in filename:
        resp = await client.get(filename)
        config.read_file(StringIO(resp.text))
        # Check if response was from cache (hishel uses extensions)
        from_cache = resp.extensions.get("from_cache", False)
        if from_cache:
            sys.stderr.write("\n  from cache")
        elif resp.status_code != 200:
            sys.stderr.write(f"\n  ERROR {resp.status_code:d}")
        else:
            sys.stderr.write("\n  fresh from server")
    else:
        raise ValueError(f"{filename} does not exist!")

    # first read own versions section
    current_version_section_name = buildout["buildout"].get("versions", "versions")
    if version_section_name is None:
        # initial name
        version_section_name = current_version_section_name
    elif version_section_name != current_version_section_name:
        # name changed, not sure if this works as expected! - jensens
        sys.stderr.write(
            "\nName of [versions] (versions = versions) has changed."
            '\nGlobal versions section name: "{gname}"'
            '\nVersions pinned under that new Section namespace "{nname}"'
            " will be ignored.".format(
                gname=version_section_name, nname=buildout["buildout"].get("versions")
            )
        )

    if filename.startswith(base_dir):
        key_name = filename[len(base_dir) + 1 :]
    else:
        key_name = filename

    # At this point version_section_name is guaranteed to be a string
    assert version_section_name is not None
    if config.has_section(version_section_name):
        version_sections[key_name] = OrderedDict(config.items(version_section_name))
        sys.stderr.write(
            f"\n  {len(version_sections[key_name]):d} entries in versions section."
        )

    # read versionannotations
    versionannotation_section_name = buildout["buildout"].get(
        "versionannotations", versionannotation_section_name
    )
    if config.has_section(versionannotation_section_name):
        annotations[key_name] = OrderedDict(
            config.items(versionannotation_section_name)
        )
        sys.stderr.write(
            f"\n  {len(annotations[key_name]):d} entries in annotations section."
        )
    try:
        extends = config.get("buildout", "extends").strip()
    except (NoSectionError, NoOptionError):
        return version_sections, annotations
    for extend in reversed(extends.splitlines()):
        extend = extend.strip()
        if not extend:
            continue
        sub_relative, extend = find_relative(extend, relative)
        await _extract_versions_section(
            client,
            extend,
            base_dir,
            version_sections,
            annotations,
            sub_relative,
            version_section_name,
            versionannotation_section_name,
        )
    return version_sections, annotations


async def parse(
    buildout_filename: str, nocache: bool = False
) -> dict[str, OrderedDict[str, dict[str, Any]]]:
    """Parse buildout configuration files and extract version information"""
    sys.stderr.write("Parsing buildout files:")
    if nocache:
        sys.stderr.write("\n(not using caches)")
    base_relative, buildout_filename = find_relative(buildout_filename)

    async with http_client(nocache=nocache) as client:
        version_sections, annotations = await _extract_versions_section(
            client, buildout_filename, relative=base_relative
        )

    sys.stderr.write("\nparsing finished.\n")
    pkgs = {}

    for name in version_sections:
        for pkg in version_sections[name]:
            if pkg not in pkgs:
                pkgs[pkg] = OrderedDict()

    for pkgname in pkgs:
        pkg = pkgs[pkgname]
        for name in version_sections:
            if pkgname in version_sections.get(name, {}):
                pkg[name] = {"v": version_sections[name][pkgname], "a": ""}

        for name in annotations:
            if pkgname in annotations.get(name, {}):
                if name in pkg:
                    pkg[name]["a"] = annotations[name][pkgname]
                else:
                    pkg[name] = {"v": None, "a": annotations[name][pkgname]}

    return pkgs
