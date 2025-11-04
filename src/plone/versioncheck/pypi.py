from collections import namedtuple
from collections import OrderedDict
from packaging.version import parse as parse_version
from packaging.version import Version
from plone.versioncheck.utils import http_client
from typing import Any

import asyncio
import datetime
import httpx
import sys


PYPI_URL = "https://pypi.org"


Release = namedtuple("Release", ["version", "release_date"])

FLOOR_RELEASE = Release(version="0.0.0.0", release_date=datetime.date(1970, 1, 1))


def mmbp_tuple(version: Version) -> list[int]:
    """major minor bugfix, postfix tuple from version

    - 1.0     -> 1.0.0.0
    - 1.2     -> 1.2.0.0
    - 1.3.4   -> 1.3.4.0
    - 1.3.4.5 -> 1.3.4.5
    """
    parts = version.base_version.split(".")
    parts += ["0"] * (4 - len(parts))
    return [int(_) for _ in parts]


async def check(
    name: str, version: str, client: httpx.AsyncClient
) -> tuple[bool | int, dict[str, Release | None] | str]:
    """Check PyPI for newer versions of a package"""  # noqa: C901
    result: OrderedDict[str, Release | None] = OrderedDict(
        [
            ("major", FLOOR_RELEASE),
            ("minor", FLOOR_RELEASE),
            ("bugfix", FLOOR_RELEASE),
            ("majorpre", FLOOR_RELEASE),
            ("minorpre", FLOOR_RELEASE),
            ("bugfixpre", FLOOR_RELEASE),
        ]
    )

    if not version:
        return False, "Empty version."

    # parse version to test against:
    try:
        version_parsed = parse_version(version)
    except Exception:
        # likely packaging.version.InvalidVersion
        # or TypeError, but really any exception can be ignored.
        # See https://github.com/plone/plone.versioncheck/issues/52
        return False, "Version broken/ not checkable."
    try:
        vtuple = mmbp_tuple(version_parsed)
    except ValueError:
        return False, "Can not check legacy version number."

    # fetch pkgs json info from pypi
    url = f"{PYPI_URL}/pypi/{name}/json"
    try:
        resp = await client.get(url)
    except Exception:
        print(f"Fatal problem while fetching URL: {url}")
        raise

    # check status code
    if resp.status_code == 404:
        return (
            False,
            f'Package "{name}" not on pypi ({url}).',
        )
    elif resp.status_code != 200:
        return False, str(resp.status_code)
    data = resp.json()

    # get information about possible updates
    releases = sorted(data["releases"])
    for release in releases:
        # major check (overall)
        try:
            rel_v = parse_version(release)
        except Exception:
            # likely packaging.version.InvalidVersion
            # but really any exception can be ignored.
            # See https://github.com/plone/plone.versioncheck/issues/52
            continue
        if rel_v <= version_parsed:
            continue
        rel_vtuple = mmbp_tuple(rel_v)
        rel_data = data["releases"][release]
        rel_date = datetime.date(1970, 1, 1)
        for rel_pkg in rel_data:
            time_string = rel_pkg.get("upload_time")
            if time_string:
                crel_date = datetime.datetime.strptime(
                    time_string, "%Y-%m-%dT%H:%M:%S"
                ).date()
                if crel_date > rel_date:
                    rel_date = crel_date
        if rel_vtuple[0] > vtuple[0]:
            if rel_v.is_prerelease and rel_v > parse_version(
                result["majorpre"].version  # type: ignore
            ):
                result["majorpre"] = Release(version=release, release_date=rel_date)
            elif not rel_v.is_prerelease and rel_v > parse_version(
                result["major"].version  # type: ignore
            ):
                result["major"] = Release(version=release, release_date=rel_date)
            continue
        if (  # Only compare same version line
            rel_vtuple[0] == vtuple[0] and rel_vtuple[1] > vtuple[1]
        ):
            if rel_v.is_prerelease and rel_v > parse_version(
                result["minorpre"].version  # type: ignore
            ):
                result["minorpre"] = Release(version=release, release_date=rel_date)
            elif not rel_v.is_prerelease and rel_v > parse_version(
                result["minor"].version  # type: ignore
            ):
                result["minor"] = Release(version=release, release_date=rel_date)
            continue
        if (  # Only compare same version line
            rel_vtuple[0] == vtuple[0]
            and rel_vtuple[1] == vtuple[1]
            and rel_vtuple[2] > vtuple[2]
        ):
            if rel_v.is_prerelease and rel_v > parse_version(
                result["bugfixpre"].version  # type: ignore
            ):
                result["bugfixpre"] = Release(version=release, release_date=rel_date)
            elif not rel_v.is_prerelease and rel_v > parse_version(
                result["bugfix"].version  # type: ignore
            ):
                result["bugfix"] = Release(version=release, release_date=rel_date)
            continue

    # reset non existing versions
    for version_tag in result:
        if result[version_tag].version == "0.0.0.0":  # type: ignore
            result[version_tag] = None

    # filter out older
    if (
        result["major"]
        and result["majorpre"]
        and parse_version(result["majorpre"].version)  # type: ignore
        < parse_version(result["major"].version)  # type: ignore
    ):
        result["majorpre"] = None
    if (
        result["minor"]
        and result["minorpre"]
        and parse_version(result["minorpre"].version)  # type: ignore
        < parse_version(result["minor"].version)  # type: ignore
    ):
        result["minorpre"] = None
    if (
        result["bugfix"]
        and result["bugfixpre"]
        and parse_version(result["bugfixpre"].version)  # type: ignore
        < parse_version(result["bugfix"].version)  # type: ignore
    ):
        result["bugfixpre"] = None

    # Check if response was from cache (hishel uses extensions)
    from_cache = resp.extensions.get("from_cache", False)
    return 2 if from_cache else 1, result


async def check_all(
    pkgsinfo: dict[str, Any],
    limit: int | None = None,
    nocache: bool = False,
    concurrency: int = 20,
) -> None:
    """Check PyPI for updates of all packages concurrently"""
    pkgs = pkgsinfo["pkgs"]
    sys.stderr.write(f"Check PyPI for updates of {len(pkgs):d} packages.")
    if limit:
        sys.stderr.write(f" Check limited to {limit:d} packages.")
    sys.stderr.write(f" (max {concurrency} concurrent)")

    pkgsinfo["pypi"] = {}
    errors = []
    semaphore = asyncio.Semaphore(concurrency)

    async def check_with_limit(
        idx: int, pkgname: str, version: str, client: httpx.AsyncClient
    ) -> tuple[int, str, tuple[bool | int, dict[str, Release | None] | str]]:
        """Check a single package with concurrency limiting"""
        async with semaphore:
            result = await check(pkgname, version, client)
            return idx, pkgname, result

    # Prepare all check tasks
    pkg_list = sorted(pkgs.items())
    if limit:
        pkg_list = pkg_list[:limit]

    async with http_client(nocache=nocache) as client:
        tasks = [
            check_with_limit(
                idx,
                pkgname,
                pkg_data[next(iter(pkg_data))]["v"],
                client,
            )
            for idx, (pkgname, pkg_data) in enumerate(pkg_list)
        ]

        # Process results as they complete
        for idx, coro in enumerate(asyncio.as_completed(tasks)):
            if idx % 20 == 0:
                sys.stderr.write(f"\n{idx:4d} ")

            task_idx, pkgname, (state, result) = await coro

            if not state:
                sys.stderr.write("E")
                current = next(iter(pkgs[pkgname]))
                errors.append((pkgname, pkgs[pkgname][current]["v"], str(result)))
                continue

            pkgsinfo["pypi"][pkgname] = result
            sys.stderr.write("O" if state == 1 else "o")

    for error in errors:
        sys.stderr.write("\nError in {} version {} reason: {}".format(*error))

    sys.stderr.write("\nPyPI check finished\n")


async def update_pkg_info(
    pkg_name: str, pkg_data: dict[str, dict[str, Any]], client: httpx.AsyncClient
) -> bool:
    """Update package information with release dates from PyPI"""
    for _filename, elemdata in pkg_data.items():
        # fetch pkgs json info from pypi
        url = f"{PYPI_URL}/pypi/{pkg_name}/json"
        resp = await client.get(url)

        # check status code
        if resp.status_code != 200:
            continue
        data = resp.json()

        rel_date = datetime.date(1970, 1, 1)
        try:
            urls = data["releases"][elemdata["v"]]
        except KeyError:
            # release not on PyPI
            continue
        for rel_pkg in urls:
            time_string = rel_pkg.get("upload_time")
            if time_string:
                crel_date = datetime.datetime.strptime(
                    time_string, "%Y-%m-%dT%H:%M:%S"
                ).date()
                if crel_date > rel_date:
                    rel_date = crel_date
        elemdata["release_date"] = rel_date

    return True


async def update_pkgs_info(
    pkgsinfo: dict[str, Any],
    limit: int | None = None,
    nocache: bool = False,
    concurrency: int = 20,
) -> None:
    """Update package information for all packages concurrently"""
    pkgs = pkgsinfo["pkgs"]
    sys.stderr.write(f"Check PyPI for data of {len(pkgs):d} packages.")
    if limit:
        sys.stderr.write(f" Check limited to {limit:d} packages.")
    sys.stderr.write(f" (max {concurrency} concurrent)")

    errors = []
    semaphore = asyncio.Semaphore(concurrency)

    async def update_with_limit(
        idx: int,
        pkg_name: str,
        pkg_data: dict[str, dict[str, Any]],
        client: httpx.AsyncClient,
    ) -> tuple[int, str, bool]:
        """Update a single package with concurrency limiting"""
        async with semaphore:
            result = await update_pkg_info(pkg_name, pkg_data, client)
            return idx, pkg_name, result

    # Prepare all update tasks
    pkg_list = list(pkgs.items())
    if limit:
        pkg_list = pkg_list[:limit]

    async with http_client(nocache=nocache) as client:
        tasks = [
            update_with_limit(idx, pkg_name, pkg_data, client)
            for idx, (pkg_name, pkg_data) in enumerate(pkg_list)
        ]

        # Process results as they complete
        for idx, coro in enumerate(asyncio.as_completed(tasks)):
            if idx % 20 == 0:
                sys.stderr.write(f"\n{idx:4d} ")

            task_idx, pkg_name, state = await coro

            if not state:
                sys.stderr.write("E")
                errors.append((pkg_name,))
                continue
            sys.stderr.write("O")

    for error in errors:
        sys.stderr.write("\nError in {}".format(*error))

    sys.stderr.write("\nPyPI check finished\n")


async def update_tracking_version_info(
    pkg_name: str, pkg_data: list[Any], client: httpx.AsyncClient
) -> tuple[bool | int, bool | str]:
    """Update tracking version information from PyPI"""
    # fetch pkgs json info from pypi
    url = f"{PYPI_URL}/pypi/{pkg_name}/{pkg_data[0]}/json"
    resp = await client.get(url)

    # check status code
    if resp.status_code == 404:
        return False, "Package Version not on pypi."
    elif resp.status_code != 200:
        return False, str(resp.status_code)
    data = resp.json()

    rel_date = datetime.date(1970, 1, 1)
    for rel_pkg in data["urls"]:
        time_string = rel_pkg.get("upload_time")
        if time_string:
            crel_date = datetime.datetime.strptime(
                time_string, "%Y-%m-%dT%H:%M:%S"
            ).date()
            if crel_date > rel_date:
                rel_date = crel_date
    # pkg_data['release_date'] = rel_date
    pkg_data.append(rel_date)

    # Check if response was from cache (hishel uses extensions)
    from_cache = resp.extensions.get("from_cache", False)
    return 2 if from_cache else 1, True


async def update_tracking_info(
    pkgsinfo: dict[str, Any], nocache: bool = False, concurrency: int = 20
) -> None:
    """Update tracking information from PyPI concurrently"""
    pkgs = pkgsinfo["tracking"]["versions"]
    sys.stderr.write(f"Check PyPI for data of {len(pkgs):d} packages.")
    sys.stderr.write(f" (max {concurrency} concurrent)")
    errors = []
    semaphore = asyncio.Semaphore(concurrency)

    async def update_tracking_with_limit(
        idx: int, pkg_name: str, pkg_data: list[Any], client: httpx.AsyncClient
    ) -> tuple[int, str, tuple[bool | int, bool | str]]:
        """Update tracking for a single package with concurrency limiting"""
        async with semaphore:
            result = await update_tracking_version_info(pkg_name, pkg_data, client)
            return idx, pkg_name, result

    # Prepare all update tasks
    pkg_list = list(pkgs.items())

    async with http_client(nocache=nocache) as client:
        tasks = [
            update_tracking_with_limit(idx, pkg_name, pkg_data, client)
            for idx, (pkg_name, pkg_data) in enumerate(pkg_list)
        ]

        # Process results as they complete
        for idx, coro in enumerate(asyncio.as_completed(tasks)):
            if idx % 20 == 0:
                sys.stderr.write(f"\n{idx:4d} ")

            task_idx, pkg_name, (state, result) = await coro

            if not state:
                sys.stderr.write("E")
                errors.append((pkg_name, str(result)))
                continue
            sys.stderr.write("O" if state == 1 else "o")

    for error in errors:
        sys.stderr.write("\nError in {} reason: {}".format(*error))

    sys.stderr.write("\nPyPI check finished\n")
