from collections import OrderedDict
from packaging.version import parse as parse_version
from plone.versioncheck.pypi import check
from plone.versioncheck.pypi import mmbp_tuple
from plone.versioncheck.pypi import PYPI_URL
from plone.versioncheck.pypi import Release

import datetime
import httpx
import pytest
import respx


def test_mmbp_tuple():
    assert mmbp_tuple(parse_version("0.0.0.0")) == [0, 0, 0, 0]
    assert mmbp_tuple(parse_version("1.0")) == [1, 0, 0, 0]
    assert mmbp_tuple(parse_version("1.1.0")) == [1, 1, 0, 0]
    assert mmbp_tuple(parse_version("0.1")) == [0, 1, 0, 0]
    assert mmbp_tuple(parse_version("0.10.1")) == [0, 10, 1, 0]
    assert mmbp_tuple(parse_version("1.1.1.1")) == [1, 1, 1, 1]
    assert mmbp_tuple(parse_version("1.1.0.a1")) == [1, 1, 0, 0]


demo_json = """{
    "info": {},
    "releases": {
        "1.0": {},
        "1.0.1": {},
        "1.0.2": {},
        "1.0.3": {},
        "1.0.4": {},
        "1.0.5": {},
        "1.0.6": {},
        "1.0.7": {},
        "1.0.8": {},
        "1.0.9": {},
        "1.0.10": {},
        "1.0.11": {},
        "1.0.12": {},
        "1.0.13.dev0": {},
        "1.1.0": {},
        "1.1.1": {},
        "1.2.0.b1": {},
        "2.0.0": {},
        "3.0.a1": {}
    }
}
"""


assumed_demo_result = OrderedDict(
    [
        ("major", Release(version="2.0.0", release_date=datetime.date(1970, 1, 1))),
        ("minor", Release(version="1.1.1", release_date=datetime.date(1970, 1, 1))),
        ("bugfix", Release(version="1.0.12", release_date=datetime.date(1970, 1, 1))),
        (
            "majorpre",
            Release(version="3.0.a1", release_date=datetime.date(1970, 1, 1)),
        ),
        (
            "minorpre",
            Release(version="1.2.0.b1", release_date=datetime.date(1970, 1, 1)),
        ),
        (
            "bugfixpre",
            Release(version="1.0.13.dev0", release_date=datetime.date(1970, 1, 1)),
        ),
    ]
)


@pytest.mark.asyncio
async def test_check():
    name = "demo"
    async with respx.mock:
        respx.get(f"{PYPI_URL}/pypi/{name}/json").mock(
            return_value=httpx.Response(200, json=eval(demo_json))
        )
        async with httpx.AsyncClient() as client:
            assert await check(name, "1.0", client) == (1, assumed_demo_result)
