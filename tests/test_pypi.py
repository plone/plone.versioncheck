from packaging.version import parse as parse_version
from plone.versioncheck.pypi import check
from plone.versioncheck.pypi import mmbp_tuple

import datetime
import httpx
import pytest
import respx


@pytest.mark.asyncio
async def test_check_empty_version():
    """Test check with empty version string"""
    async with httpx.AsyncClient() as client:
        result = await check("somepackage", "", client)
        assert result == (False, "Empty version.")


@pytest.mark.asyncio
async def test_check_invalid_version():
    """Test check with invalid/broken version"""
    async with httpx.AsyncClient() as client:
        result = await check("somepackage", ">= 1.0", client)
        assert result[0] is False
        assert "broken" in result[1].lower() or "not checkable" in result[1].lower()


@pytest.mark.asyncio
@respx.mock
async def test_check_package_not_found():
    """Test check when package doesn't exist on PyPI"""
    respx.get("https://pypi.org/pypi/nonexistent/json").mock(
        return_value=httpx.Response(404)
    )

    async with httpx.AsyncClient() as client:
        result = await check("nonexistent", "1.0.0", client)
        assert result[0] is False
        assert "not on pypi" in result[1].lower()


@pytest.mark.asyncio
@respx.mock
async def test_check_pypi_server_error():
    """Test check when PyPI returns server error"""
    respx.get("https://pypi.org/pypi/somepackage/json").mock(
        return_value=httpx.Response(500)
    )

    async with httpx.AsyncClient() as client:
        result = await check("somepackage", "1.0.0", client)
        assert result[0] is False
        assert result[1] == "500"


@pytest.mark.asyncio
@respx.mock
async def test_check_no_newer_versions():
    """Test check when current version is latest"""
    mock_response = {
        "releases": {
            "1.0.0": [{"upload_time": "2020-01-01T00:00:00"}],
            "0.9.0": [{"upload_time": "2019-01-01T00:00:00"}],
        }
    }
    respx.get("https://pypi.org/pypi/somepackage/json").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    async with httpx.AsyncClient() as client:
        result = await check("somepackage", "1.0.0", client)
        assert result[0] == 1
        # All categories should be None (no updates)
        updates = result[1]
        assert updates["major"] is None
        assert updates["minor"] is None
        assert updates["bugfix"] is None


@pytest.mark.asyncio
@respx.mock
async def test_check_bugfix_update_available():
    """Test check when bugfix update is available"""
    mock_response = {
        "releases": {
            "1.0.0": [{"upload_time": "2020-01-01T00:00:00"}],
            "1.0.1": [{"upload_time": "2020-02-01T12:30:45"}],
        }
    }
    respx.get("https://pypi.org/pypi/somepackage/json").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    async with httpx.AsyncClient() as client:
        result = await check("somepackage", "1.0.0", client)
        assert result[0] == 1
        updates = result[1]
        assert updates["bugfix"].version == "1.0.1"
        assert updates["bugfix"].release_date == datetime.date(2020, 2, 1)
        assert updates["minor"] is None
        assert updates["major"] is None


@pytest.mark.asyncio
@respx.mock
async def test_check_minor_update_available():
    """Test check when minor update is available"""
    mock_response = {
        "releases": {
            "1.0.0": [{"upload_time": "2020-01-01T00:00:00"}],
            "1.1.0": [{"upload_time": "2020-03-01T00:00:00"}],
        }
    }
    respx.get("https://pypi.org/pypi/somepackage/json").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    async with httpx.AsyncClient() as client:
        result = await check("somepackage", "1.0.0", client)
        assert result[0] == 1
        updates = result[1]
        assert updates["minor"].version == "1.1.0"
        assert updates["major"] is None


@pytest.mark.asyncio
@respx.mock
async def test_check_major_update_available():
    """Test check when major update is available"""
    mock_response = {
        "releases": {
            "1.0.0": [{"upload_time": "2020-01-01T00:00:00"}],
            "2.0.0": [{"upload_time": "2021-01-01T00:00:00"}],
        }
    }
    respx.get("https://pypi.org/pypi/somepackage/json").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    async with httpx.AsyncClient() as client:
        result = await check("somepackage", "1.0.0", client)
        assert result[0] == 1
        updates = result[1]
        assert updates["major"].version == "2.0.0"


@pytest.mark.asyncio
@respx.mock
async def test_check_prerelease_versions():
    """Test check with prerelease versions (alpha, beta, rc)"""
    mock_response = {
        "releases": {
            "1.0.0": [{"upload_time": "2020-01-01T00:00:00"}],
            "1.0.1rc1": [{"upload_time": "2020-02-01T00:00:00"}],
            "1.1.0a1": [{"upload_time": "2020-03-01T00:00:00"}],
            "2.0.0b1": [{"upload_time": "2020-04-01T00:00:00"}],
        }
    }
    respx.get("https://pypi.org/pypi/somepackage/json").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    async with httpx.AsyncClient() as client:
        result = await check("somepackage", "1.0.0", client)
        assert result[0] == 1
        updates = result[1]
        # Prereleases should be categorized separately
        assert updates["bugfixpre"].version == "1.0.1rc1"
        assert updates["minorpre"].version == "1.1.0a1"
        assert updates["majorpre"].version == "2.0.0b1"


@pytest.mark.asyncio
@respx.mock
async def test_check_invalid_version_in_releases():
    """Test check when PyPI data contains invalid versions"""
    mock_response = {
        "releases": {
            "1.0.0": [{"upload_time": "2020-01-01T00:00:00"}],
            "invalid-version": [{"upload_time": "2020-02-01T00:00:00"}],
            "1.1.0": [{"upload_time": "2020-03-01T00:00:00"}],
        }
    }
    respx.get("https://pypi.org/pypi/somepackage/json").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    async with httpx.AsyncClient() as client:
        result = await check("somepackage", "1.0.0", client)
        # Should skip invalid version and find 1.1.0
        assert result[0] == 1
        updates = result[1]
        assert updates["minor"].version == "1.1.0"


@pytest.mark.asyncio
@respx.mock
async def test_check_release_without_upload_time():
    """Test check when release has no upload_time"""
    mock_response = {
        "releases": {
            "1.0.0": [{"upload_time": "2020-01-01T00:00:00"}],
            "1.0.1": [{}],  # No upload_time
        }
    }
    respx.get("https://pypi.org/pypi/somepackage/json").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    async with httpx.AsyncClient() as client:
        result = await check("somepackage", "1.0.0", client)
        assert result[0] == 1
        updates = result[1]
        # Should still detect the version even without date
        assert updates["bugfix"].version == "1.0.1"
        assert updates["bugfix"].release_date == datetime.date(1970, 1, 1)


@pytest.mark.asyncio
@respx.mock
async def test_check_multiple_releases_same_version():
    """Test check when version has multiple releases with different dates"""
    mock_response = {
        "releases": {
            "1.0.0": [{"upload_time": "2020-01-01T00:00:00"}],
            "1.0.1": [
                {"upload_time": "2020-02-01T00:00:00"},
                {"upload_time": "2020-02-15T00:00:00"},  # Later date
            ],
        }
    }
    respx.get("https://pypi.org/pypi/somepackage/json").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    async with httpx.AsyncClient() as client:
        result = await check("somepackage", "1.0.0", client)
        assert result[0] == 1
        updates = result[1]
        # Should use the latest date
        assert updates["bugfix"].release_date == datetime.date(2020, 2, 15)


def test_mmbp_tuple_two_parts():
    """Test mmbp_tuple with major.minor version"""
    version = parse_version("1.2")
    result = mmbp_tuple(version)
    assert result == [1, 2, 0, 0]


def test_mmbp_tuple_three_parts():
    """Test mmbp_tuple with major.minor.bugfix version"""
    version = parse_version("1.2.3")
    result = mmbp_tuple(version)
    assert result == [1, 2, 3, 0]


def test_mmbp_tuple_four_parts():
    """Test mmbp_tuple with major.minor.bugfix.patch version"""
    version = parse_version("1.2.3.4")
    result = mmbp_tuple(version)
    assert result == [1, 2, 3, 4]


def test_mmbp_tuple_one_part():
    """Test mmbp_tuple with major version only"""
    version = parse_version("3")
    result = mmbp_tuple(version)
    assert result == [3, 0, 0, 0]


def test_mmbp_tuple_with_prerelease():
    """Test mmbp_tuple ignores prerelease suffix"""
    version = parse_version("1.2.3rc1")
    result = mmbp_tuple(version)
    # Should use base_version which strips rc1
    assert result == [1, 2, 3, 0]


@pytest.mark.asyncio
@respx.mock
async def test_update_pkg_info_success():
    """Test update_pkg_info successfully updates release dates"""
    from plone.versioncheck.pypi import update_pkg_info

    mock_response = {
        "releases": {
            "1.0.0": [
                {"upload_time": "2020-01-01T00:00:00"},
                {"upload_time": "2020-01-15T12:30:00"},  # Latest
            ]
        }
    }
    respx.get("https://pypi.org/pypi/testpkg/json").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    pkg_data = {"buildout.cfg": {"v": "1.0.0"}}
    async with httpx.AsyncClient() as client:
        result = await update_pkg_info("testpkg", pkg_data, client)

    assert result is True
    assert pkg_data["buildout.cfg"]["release_date"] == datetime.date(2020, 1, 15)


@pytest.mark.asyncio
@respx.mock
async def test_update_pkg_info_not_found():
    """Test update_pkg_info handles missing packages gracefully"""
    from plone.versioncheck.pypi import update_pkg_info

    respx.get("https://pypi.org/pypi/testpkg/json").mock(
        return_value=httpx.Response(404)
    )

    pkg_data = {"buildout.cfg": {"v": "1.0.0"}}
    async with httpx.AsyncClient() as client:
        result = await update_pkg_info("testpkg", pkg_data, client)

    # Should return True but not add release_date
    assert result is True
    assert "release_date" not in pkg_data["buildout.cfg"]


@pytest.mark.asyncio
@respx.mock
async def test_update_pkg_info_version_not_on_pypi():
    """Test update_pkg_info when specific version not in releases"""
    from plone.versioncheck.pypi import update_pkg_info

    mock_response = {
        "releases": {
            "2.0.0": [{"upload_time": "2021-01-01T00:00:00"}]
            # 1.0.0 not in releases
        }
    }
    respx.get("https://pypi.org/pypi/testpkg/json").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    pkg_data = {"buildout.cfg": {"v": "1.0.0"}}
    async with httpx.AsyncClient() as client:
        result = await update_pkg_info("testpkg", pkg_data, client)

    assert result is True
    # Should not add release_date since version not found
    assert "release_date" not in pkg_data["buildout.cfg"]


@pytest.mark.asyncio
@respx.mock
async def test_update_tracking_version_info_success():
    """Test update_tracking_version_info successfully updates tracking data"""
    from plone.versioncheck.pypi import update_tracking_version_info

    mock_response = {
        "urls": [
            {"upload_time": "2020-01-01T00:00:00"},
            {"upload_time": "2020-01-10T00:00:00"},  # Latest
        ]
    }
    respx.get("https://pypi.org/pypi/testpkg/1.0.0/json").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    pkg_data = ["1.0.0"]
    async with httpx.AsyncClient() as client:
        state, result = await update_tracking_version_info("testpkg", pkg_data, client)

    assert state == 1  # 1 for non-cached
    assert result is True
    assert pkg_data[1] == datetime.date(2020, 1, 10)


@pytest.mark.asyncio
@respx.mock
async def test_update_tracking_version_info_not_found():
    """Test update_tracking_version_info handles 404 errors"""
    from plone.versioncheck.pypi import update_tracking_version_info

    respx.get("https://pypi.org/pypi/testpkg/1.0.0/json").mock(
        return_value=httpx.Response(404)
    )

    pkg_data = ["1.0.0"]
    async with httpx.AsyncClient() as client:
        state, result = await update_tracking_version_info("testpkg", pkg_data, client)

    assert state is False
    assert result == "Package Version not on pypi."


@pytest.mark.asyncio
@respx.mock
async def test_update_tracking_version_info_server_error():
    """Test update_tracking_version_info handles server errors"""
    from plone.versioncheck.pypi import update_tracking_version_info

    respx.get("https://pypi.org/pypi/testpkg/1.0.0/json").mock(
        return_value=httpx.Response(500)
    )

    pkg_data = ["1.0.0"]
    async with httpx.AsyncClient() as client:
        state, result = await update_tracking_version_info("testpkg", pkg_data, client)

    assert state is False
    assert result == "500"


@pytest.mark.asyncio
@respx.mock
async def test_check_all_single_package(capsys):
    """Test check_all with a single package"""
    from plone.versioncheck.pypi import check_all

    mock_response = {
        "releases": {
            "1.0.0": [{"upload_time": "2020-01-01T00:00:00"}],
            "1.1.0": [{"upload_time": "2020-02-01T00:00:00"}],
        }
    }
    respx.get("https://pypi.org/pypi/testpkg/json").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    pkgsinfo = {"pkgs": {"testpkg": {"buildout.cfg": {"v": "1.0.0"}}}}

    await check_all(pkgsinfo, nocache=True)

    assert "pypi" in pkgsinfo
    assert "testpkg" in pkgsinfo["pypi"]
    assert pkgsinfo["pypi"]["testpkg"]["minor"].version == "1.1.0"

    captured = capsys.readouterr()
    assert "Check PyPI for updates" in captured.err
    assert "PyPI check finished" in captured.err


@pytest.mark.asyncio
@respx.mock
async def test_check_all_with_limit(capsys):
    """Test check_all with package limit"""
    from plone.versioncheck.pypi import check_all

    mock_response = {"releases": {"1.0.0": [{"upload_time": "2020-01-01T00:00:00"}]}}
    respx.get(url__regex=r"https://pypi\.org/pypi/.*/json").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    pkgsinfo = {
        "pkgs": {
            "pkg1": {"buildout.cfg": {"v": "1.0.0"}},
            "pkg2": {"buildout.cfg": {"v": "1.0.0"}},
            "pkg3": {"buildout.cfg": {"v": "1.0.0"}},
        }
    }

    await check_all(pkgsinfo, limit=2, nocache=True)

    # Only 2 packages should be checked
    assert len(pkgsinfo["pypi"]) == 2

    captured = capsys.readouterr()
    assert "Check limited to 2 packages" in captured.err


@pytest.mark.asyncio
@respx.mock
async def test_check_all_with_error(capsys):
    """Test check_all handles package errors"""
    from plone.versioncheck.pypi import check_all

    # First package succeeds
    respx.get("https://pypi.org/pypi/goodpkg/json").mock(
        return_value=httpx.Response(
            200, json={"releases": {"1.0.0": [{"upload_time": "2020-01-01T00:00:00"}]}}
        )
    )

    # Second package fails
    respx.get("https://pypi.org/pypi/badpkg/json").mock(
        return_value=httpx.Response(404)
    )

    pkgsinfo = {
        "pkgs": {
            "goodpkg": {"buildout.cfg": {"v": "1.0.0"}},
            "badpkg": {"buildout.cfg": {"v": "1.0.0"}},
        }
    }

    await check_all(pkgsinfo, nocache=True)

    # Only good package should be in results
    assert "goodpkg" in pkgsinfo["pypi"]
    assert "badpkg" not in pkgsinfo["pypi"]

    captured = capsys.readouterr()
    assert "Error in badpkg" in captured.err
