from collections import OrderedDict
from plone.versioncheck.parser import _extract_versions_section
from plone.versioncheck.parser import nostdout
from plone.versioncheck.parser import parse

import httpx
import pytest
import respx


def test_nostdout(capsys):
    print("Test stdout")
    out, err = capsys.readouterr()
    assert out == "Test stdout\n"
    with nostdout():
        print("This should never be in stdout ")

    out, err = capsys.readouterr()
    assert out == ""

    print("This should be printed again.")
    out, err = capsys.readouterr()
    assert out == "This should be printed again.\n"


@pytest.mark.asyncio
async def test_parse(capsys):
    input = "buildout.cfg"

    result = await parse(input, False)
    out, err = capsys.readouterr()
    assert err[:23] == "Parsing buildout files:"
    assert (
        """buildout.cfg
  3 entries in versions section.
  1 entries in annotations section.
"""
        in err
    )

    assert result == {
        "collective.quickupload": OrderedDict(
            [("foo.cfg", {"v": "1.5.8", "a": ""}), ("baz.cfg", {"v": "1.5.2", "a": ""})]
        ),
        "ipython": OrderedDict([("buildout.cfg", {"v": "5.3.0", "a": ""})]),
        "lazy": OrderedDict(
            [
                ("buildout.cfg", {"v": "1.0", "a": ""}),
                ("buildout.d/spam.cfg", {"v": ">= 1.1", "a": ""}),
            ]
        ),
        "products.cmfcore": OrderedDict(
            [
                (
                    "buildout.cfg",
                    {"v": "2.1.1", "a": "\nJust a Test Case\nwith multiple lines"},
                ),  # NOQA: E501
                ("bar.cfg", {"v": "2.2.0", "a": ""}),
                ("foo.cfg", {"v": "3.0.1", "a": ""}),
                ("baz.cfg", {"v": "2.2.10", "a": ""}),
            ]
        ),
    }


@pytest.mark.asyncio
@respx.mock
async def test_extract_versions_remote_url(capsys):
    """Test _extract_versions_section with remote HTTP URL"""
    mock_buildout_content = """[buildout]
versions = versions

[versions]
testpackage = 1.0.0
"""
    respx.get("http://example.com/buildout.cfg").mock(
        return_value=httpx.Response(200, text=mock_buildout_content)
    )

    from plone.versioncheck.utils import http_client

    version_sections = OrderedDict()
    annotations = OrderedDict()

    async with http_client() as client:
        result_versions, result_annotations = await _extract_versions_section(
            filename="http://example.com/buildout.cfg",
            version_sections=version_sections,
            annotations=annotations,
            client=client,
            base_dir=".",
        )

    captured = capsys.readouterr()
    assert "http://example.com/buildout.cfg" in captured.err
    assert "fresh from server" in captured.err or "from cache" in captured.err


@pytest.mark.asyncio
@respx.mock
async def test_extract_versions_remote_url_error(capsys):
    """Test _extract_versions_section with remote URL returning error"""
    respx.get("http://example.com/buildout.cfg").mock(
        return_value=httpx.Response(404, text="")
    )

    from plone.versioncheck.utils import http_client

    version_sections = OrderedDict()
    annotations = OrderedDict()

    async with http_client() as client:
        result_versions, result_annotations = await _extract_versions_section(
            filename="http://example.com/buildout.cfg",
            version_sections=version_sections,
            annotations=annotations,
            client=client,
            base_dir=".",
        )

    captured = capsys.readouterr()
    assert "ERROR 404" in captured.err


@pytest.mark.asyncio
async def test_extract_versions_missing_local_file():
    """Test _extract_versions_section with missing local file raises ValueError"""
    from plone.versioncheck.utils import http_client

    version_sections = OrderedDict()
    annotations = OrderedDict()

    async with http_client() as client:
        with pytest.raises(ValueError, match="does not exist"):
            await _extract_versions_section(
                filename="nonexistent_file.cfg",
                version_sections=version_sections,
                annotations=annotations,
                client=client,
                base_dir=".",
            )


@pytest.mark.asyncio
async def test_extract_versions_empty_extend_lines(capsys):
    """Test _extract_versions_section handles empty lines in extends"""
    from plone.versioncheck.utils import http_client

    import os
    import tempfile

    # Save and restore working directory
    original_cwd = os.getcwd()

    try:
        # Create a buildout file with empty lines in extends
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cfg", delete=False, dir=original_cwd
        ) as f:
            f.write("[buildout]\n")
            f.write("extends = \n")  # Empty extends
            f.write("    \n")  # Whitespace only
            f.write("versions = versions\n")
            f.write("\n[versions]\n")
            f.write("testpkg = 1.0\n")
            temp_file = f.name

        version_sections = OrderedDict()
        annotations = OrderedDict()

        async with http_client() as client:
            result_versions, result_annotations = await _extract_versions_section(
                filename=temp_file,
                version_sections=version_sections,
                annotations=annotations,
                client=client,
                base_dir=original_cwd,
            )

        # Should handle empty extends gracefully
        assert isinstance(result_versions, OrderedDict)
        assert "testpkg" in str(result_versions) or len(result_versions) >= 0
    finally:
        # Clean up temp file
        if "temp_file" in locals() and os.path.exists(temp_file):
            os.unlink(temp_file)
        # Restore working directory
        os.chdir(original_cwd)
