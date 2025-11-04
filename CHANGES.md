# Changelog

## 2.0.1

### Bug fixes

- Update workflows and docs to use 'main' as default branch [jensens]
- Fix uv cache configuration in CI workflows. [jensens]

## 2.0.0

### Breaking changes

- Drop Python 2.7 and Python 3.9 support. Require Python 3.10 or later.
  [jensens]
- Replace `requests` library with `httpx` for async HTTP support.
  [jensens]
- Convert all HTTP operations to async (requires no user code changes).
  [jensens]

### New features

- **10-50x performance improvement** for PyPI checks through concurrent async HTTP requests.
  [jensens]
- Add comprehensive type hints throughout the codebase (PEP 484).
  [jensens]
- Modernize build system: use `pyproject.toml` with `setuptools` backend (PEP 621).
  Changed from `hatchling` to `setuptools` for compatibility with `zc.buildout` develop installs.
  [jensens]
- Add upper bound version constraint for `httpx` dependency (`httpx>=0.27,<1.0`).
  This prevents installation of `httpx==1.0dev3` which has breaking API changes (missing `AsyncClient`).
  [jensens]
- Add GitHub Actions CI/CD workflows for testing, linting, and automated releases.
  [jensens]
- Configure PyPI Trusted Publishing for secure, token-free releases.
  [jensens]
- Replace `black`/`mypy` with `ruff`/`pyright` for faster linting and type checking.
  [jensens]
- Add `pre-commit` configuration with `ruff`, `isort` (plone profile), and `pyright`.
  [jensens]
- Add concurrency control for PyPI requests (default: 20 concurrent).
  [jensens]
- Convert to PEP 420 implicit namespace packages.
  [jensens]
- Add comprehensive test coverage (pypi.py: 26 tests, utils.py: 25 tests, parser.py: 4 new tests).
  [jensens]
- Increase test coverage from 65% to 77% with better edge case testing.
  [jensens]
- Increase minimum coverage requirement from 60% to 77% in test suite.
  [jensens]
- Add separate lint and type-check jobs to CI workflow for better feedback.
  [jensens]
- Use official pyright-action for CI type checking with PR annotations.
  [jensens]

### Bug fixes

- Fix invalid version handling when using `packaging` library.
  [jensens]
- Replace deprecated `pkg_resources` with `packaging` library.
  [jensens]

## 1.8.2 (2024-10-23)

### Bug fixes

- Fix for Python 3.12: configparser removed "readfp()"
  [petschki]

## 1.8.1 (2023-05-08)

### Bug fixes

- Catch empty version and ignore invalid versions in more places.
  Needed when a package is explicitly unpinned, for example `Zope =`.
  [maurits]

## 1.8.0 (2023-04-15)

- Ignore invalid versions.
  Needed for `setuptools` 66 and higher when checking a package that has invalid versions on PyPI.
  Fixes [issue 52](https://github.com/plone/plone.versioncheck/issues/52).
  [maurits]

## 1.7.0 (2019-03-08)

- Feature: Offers exclude pattern matching for cfg-files.
  [jensens]

- Use pure black as code style.
  [jensens]

- Test on Python 3.7
  [jensens]

- Fix PyPI url and add output of URL in case of a problem.
  [jensens]

## 1.6.10 (2018-08-20)

- Fixes another bug in `find_relative`.
  [jensens]

## 1.6.9 (2018-08-20)

- Fixes bug in `find_relative` introduced in last release.
  [jensens]

## 1.6.8 (2018-08-14)

### Bug fixes

- Better handling of relative paths as entry, like `project/foo/dev.cfg`.
  [jensens]

- If a file does not extend any other file,
  the return statement was returning only one parameter,
  while callers expected 2.
  [gforcada]

## 1.6.7 (2018-03-26)

### Bug fixes

- Fix: Do not trust on setuptools internals.
  Works now with newest setuptools.
  [jensens]

## 1.6.6 (2018-01-26)

- Fixed: Inherited extends with same name showed up as same.
  Now show relative to basedir if possible, else full.
  [jensens]

- Fixed: Relative extends in urls were broken.
  [jensens]

## 1.6.5 (2017-07-03)

### Bug fixes

- Relative Paths should work now, tested with subdirectories.
  [loechel]

## 1.6.4 (2017-05-08)

- Fix: Default versions section name `versions` was not respected.
  [jensens]

## 1.6.3 (2017-05-05)

- Fixes #17: Requirements were missing.
  [jensens]

- Optimization: Reduce load on PyPI when fetching release dates.
  [jensens]

- Feature: Change package and version fields in html output to links so that you could open pypi page for each package.
  [loechel]

## 1.6.2 (2017-04-12)

- Fix: Regressions with version-annotations and stdout messages from buildout parser.
  [loechel]

- Add more Tests
  [loechel]

## 1.6.1 (2017-04-07)

- Fix: #36 New buildout parser does not work with buildout.coredev
  [loechel]

## 1.6.0 (2017-04-07)

- Fix: `IndexError: string index out of range` error with empty states in the formatter.
  [thet]

- Development: Added basic tests to package.
  [loechel]

- Fix: Changed parser.py to use functions from zc.buildout to get versions and versionannotations section names.
  [loechel]

- Feature: Add function to extract date information from PyPI to analyze package age.
  [loechel]

- Feature: Add new CLI options for an output file and show release dates.
  [loechel]

## 1.5.1 (2017-01-23)

- Fix Version Compare.
  [loechel]

## 1.5.0 (2016-10-15)

- Development: Use code analysis for QA (and fix issues with pep8 et al.)
  [jensens]

- Fix: Manifest (jinja file was missing).
  [jensens]

- Feature: Implement #25: Annotate versions used.
  [jensens]

## 1.4 (2016-09-30)

- Feature:
  New option '-N': feature to hide orphaned without updates.
  This reduces the noise in a environment where orphaned are used by intend.
  [jensens]

## 1.3 (2016-05-19)

- Development: Add .editorconfig File to maintain code conventions following Plone API
  [loechel]

- Feature: Add Support for Python 3
  [loechel]

- Fix: Various documentation typos.
  [jean]

## 1.2.1 (2016-01-26)

- Feature: Cache buildout cfg files fetched over the network.
  [jensens]

- Feature: It caches now responses from PyPI.
  [jensens]

## 1.1.2 (2016-01-21)

- Fix: Resolution order buildout extends chain was wrong. Also documented the
  resolution order and included in own buildout a small example.
  [jensens]

- Fix: Formatter printed a newline to much after `required by`.
  [jensens]

- Fix: Do not complain about missing track file. If it is not there,
  the buildout is simply not using the buildout extension. [maurits]

- Fix #13: Added missing `zc.buildout` requirement. [maurits]

## 1.1.1 (2016-01-20)

- Fix: Orphan detection failed when no tracking file was present.
  [jensens]

- Fix: Exception raised when no tracking file was present.
  [jensens]

- Fix: Color of requirements was not set explicitly.
  [jensens]

## 1.1 (2016-01-19)

- Enhancement: show requirements
  [jensens]

- Enhancement: machine readable output (json)
  [jensens]

- Enhancement: write pure processing-info output to sys.stderr
  [jensens]

- Fix #5 - Require setuptools>=12
  [jensens]

- Fix #7 - Available update from 'lazy' 1.0 to 1.2 is not found.
  [jensens]

- Enhancement: Rethink colors and document them, fixes #2 and #3.
  [jensens]

- Enhancement: display output and show tracked info
  [jensens]

- Feature: Add buildout extension to optional track required by and if its use at all
  [jensens]

## 1.0 (2016-01-13)

- Initial work.
  [jensens]
