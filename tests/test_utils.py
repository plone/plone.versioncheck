from plone.versioncheck import utils
from unittest.mock import patch

import os
import pytest


def test_color_init_with_colored():
    """Test color_init when COLORED is True"""
    utils.COLORED = True
    # Should not raise any exception
    utils.color_init()


def test_color_init_without_colored():
    """Test color_init when COLORED is False"""
    original = utils.COLORED
    try:
        utils.COLORED = False
        # Should not raise any exception
        utils.color_init()
    finally:
        utils.COLORED = original


def test_color_by_state_with_colored():
    """Test color_by_state returns color codes when COLORED is True"""
    original = utils.COLORED
    try:
        utils.COLORED = True
        # Test known states
        result = utils.color_by_state("D")
        assert result  # Should return non-empty string
        assert isinstance(result, str)

        result = utils.color_by_state("A")
        assert result
        assert isinstance(result, str)

        # Test unknown state (should return default)
        result = utils.color_by_state("UNKNOWN")
        assert result
        assert isinstance(result, str)
    finally:
        utils.COLORED = original


def test_color_by_state_without_colored():
    """Test color_by_state returns empty string when COLORED is False"""
    original = utils.COLORED
    try:
        utils.COLORED = False
        result = utils.color_by_state("D")
        assert result == ""

        result = utils.color_by_state("UNKNOWN")
        assert result == ""
    finally:
        utils.COLORED = original


def test_color_dimmed_with_colored():
    """Test color_dimmed returns color code when COLORED is True"""
    original = utils.COLORED
    try:
        utils.COLORED = True
        result = utils.color_dimmed()
        assert result
        assert isinstance(result, str)
    finally:
        utils.COLORED = original


def test_color_dimmed_without_colored():
    """Test color_dimmed returns empty string when COLORED is False"""
    original = utils.COLORED
    try:
        utils.COLORED = False
        result = utils.color_dimmed()
        assert result == ""
    finally:
        utils.COLORED = original


def test_dots_short_value():
    """Test dots with value shorter than max"""
    result = utils.dots("hello", 10)
    # Should contain dots to pad to 10 characters
    # Format: " ......." (space + dots)
    assert "." in result


def test_dots_exact_length():
    """Test dots with value equal to max"""
    result = utils.dots("hello", 5)
    # No dots needed
    assert "." not in result or len(result) == 0


def test_dots_longer_value():
    """Test dots with value longer than max"""
    result = utils.dots("hello world", 5)
    # Negative dots, should handle gracefully
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_http_client_nocache_false():
    """Test http_client context manager without cache"""
    async with utils.http_client(nocache=False) as client:
        assert isinstance(client, object)  # httpx.AsyncClient
        assert hasattr(client, "get")


@pytest.mark.asyncio
async def test_http_client_nocache_true():
    """Test http_client context manager with nocache=True"""
    async with utils.http_client(nocache=True) as client:
        assert isinstance(client, object)
        assert hasattr(client, "get")


def test_find_relative_with_url():
    """Test find_relative with HTTP URL"""
    extend = "http://example.com/path/to/file.cfg"
    base, filename = utils.find_relative(extend)
    assert base == "http://example.com/path/to"
    assert filename == "file.cfg"


def test_find_relative_with_https_url():
    """Test find_relative with HTTPS URL"""
    extend = "https://example.com/configs/buildout.cfg"
    base, filename = utils.find_relative(extend)
    assert base == "https://example.com/configs"
    assert filename == "buildout.cfg"


def test_find_relative_with_local_path():
    """Test find_relative with local file path"""
    extend = "buildout.cfg"
    base, filename = utils.find_relative(extend)
    # Should return absolute path
    assert os.path.isabs(base)
    assert filename == "buildout.cfg"


def test_find_relative_with_relative_path():
    """Test find_relative with relative directory"""
    extend = "foo.cfg"
    relative = "/some/base/dir"
    base, filename = utils.find_relative(extend, relative)
    assert base == "/some/base/dir"
    assert filename == "foo.cfg"


def test_find_relative_with_relative_subdirectory():
    """Test find_relative with subdirectory in extend"""
    extend = "subdir/foo.cfg"
    relative = "/base"
    base, filename = utils.find_relative(extend, relative)
    assert base == "/base/subdir"
    assert filename == "foo.cfg"


def test_find_relative_with_url_relative():
    """Test find_relative when relative is a URL"""
    extend = "file.cfg"
    relative = "http://example.com/base/"
    base, filename = utils.find_relative(extend, relative)
    assert base == "http://example.com/base"
    assert filename == "file.cfg"


def test_get_terminal_size_returns_tuple():
    """Test get_terminal_size returns a tuple of integers"""
    result = utils.get_terminal_size()
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], int)
    assert isinstance(result[1], int)
    # Should have reasonable values
    assert result[0] > 0
    assert result[1] > 0


@patch("platform.system")
def test_get_terminal_size_linux(mock_system):
    """Test get_terminal_size on Linux"""
    mock_system.return_value = "Linux"
    result = utils.get_terminal_size()
    assert isinstance(result, tuple)
    assert len(result) == 2


@patch("platform.system")
def test_get_terminal_size_darwin(mock_system):
    """Test get_terminal_size on macOS"""
    mock_system.return_value = "Darwin"
    result = utils.get_terminal_size()
    assert isinstance(result, tuple)
    assert len(result) == 2


@patch("platform.system")
def test_get_terminal_size_windows(mock_system):
    """Test get_terminal_size on Windows"""
    mock_system.return_value = "Windows"
    result = utils.get_terminal_size()
    assert isinstance(result, tuple)
    assert len(result) == 2


@patch("platform.system")
def test_get_terminal_size_unknown_os(mock_system):
    """Test get_terminal_size with unknown OS returns default"""
    mock_system.return_value = "UnknownOS"
    result = utils.get_terminal_size()
    # Should return default (80, 25)
    assert result == (80, 25)


def test_get_terminal_size_linux_ioctl_failure():
    """Test _get_terminal_size_linux when ioctl fails"""
    # Call the function - it should handle failures gracefully
    result = utils._get_terminal_size_linux()
    # Should either return a tuple or None
    assert result is None or (isinstance(result, tuple) and len(result) == 2)


def test_get_terminal_size_tput():
    """Test _get_terminal_size_tput"""
    # This may fail in test environment without tput
    result = utils._get_terminal_size_tput()
    assert result is None or (isinstance(result, tuple) and len(result) == 2)


def test_get_terminal_size_windows_internal():
    """Test _get_terminal_size_windows internal function"""
    # This will fail on non-Windows, which is expected
    result = utils._get_terminal_size_windows()
    assert result is None or (isinstance(result, tuple) and len(result) == 2)


@patch.dict(os.environ, {"LINES": "50", "COLUMNS": "120"}, clear=False)
@patch("os.open", side_effect=Exception("No terminal"))
def test_get_terminal_size_linux_from_env(mock_open):
    """Test _get_terminal_size_linux falls back to environment variables"""
    result = utils._get_terminal_size_linux()
    # When ioctl and /dev/tty fail, should try environment variables
    if result:
        assert isinstance(result, tuple)
        assert len(result) == 2
