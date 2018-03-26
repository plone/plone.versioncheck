Changelog
=========

1.6.7 (2018-03-26)
------------------

Bug fixes:

- Fix: Do not trust on setuptools internals. 
  Works now with newest setuptools.
  [jensens]

1.6.6 (2018-01-26)
------------------

Breaking changes:

- *add item here*

New features:

- *add item here*

Bug fixes:

- Fixed: Inherited extends with same name showed up as same.
  Now show relative to basedir if possible, else full.
  [jensens]

- Fixed: Relative extends in urls were broken.
  [jensens]


1.6.5 (2017-07-03)
------------------

Bug fixes:

- Relative Paths should work now, tested with subdirectories.
  [loechel]


1.6.4 (2017-05-08)
------------------

- Fix: Default versions section name ``versions`` was not respected.
  [jensens]


1.6.3 (2017-05-05)
------------------

- Fixes #17: Requirements were missing.
  [jensens]

- Optimization: Reduce load on PyPI when fetching release dates.
  [jensens]

- Feature: Change package and version fields in html output to links so that you could open pypi page for each package.
  [loechel]


1.6.2 (2017-04-12)
------------------

- Fix: Regressions with version-annotations and stdout messages from buildout parser.
  [loechel]

- Add more Tests
  [loechel]

1.6.1 (2017-04-07)
------------------

- Fix: #36 New buildout parser does not work with buildout.coredev
  [loechel]

1.6.0 (2017-04-07)
------------------

- Fix: ``IndexError: string index out of range`` error with empty states in the formatter.
  [thet]

- Development: Added basic tests to package.
  [loechel]

- Fix: Changed parser.py to use functions from zc.buildout to get versions and versionannotations section names.
  [loechel]

- Feature: Add function to extract date information from PyPI to analyze package age.
  [loechel]

- Feature: Add new CLI options for an output file and show release dates.
  [loechel]

1.5.1 (2017-01-23)
------------------

- Fix Version Compare.
  [loechel]

1.5.0 (2016-10-15)
------------------

- Development: Use code analysis for QA (and fix issues with pep8 et al.)
  [jensens]

- Fix: Manifest (jinja file was missing).
  [jensens]

- Feature: Implement #25: Annotate versions used.
  [jensens]


1.4 (2016-09-30)
----------------

- Feature:
  New option '-N': feature to hide orphaned without updates.
  This reduces the noise in a environment where orphaned are used by intend.
  [jensens]


1.3 (2016-05-19)
----------------

- Development: Add .editorconfig File to maintain code convetions following Plone API
  [loechel]

- Feature: Add Support for Python 3
  [loechel]

- Fix: Various documentation typos.
  [jean]

1.2.1 (2016-01-26)
------------------

- Feature: Cache buildout cfg files fetched over the network.
  [jensens]

- Feature: It caches now responses from PyPI.
  [jensens]


1.1.2 (2016-01-21)
------------------

- Fix: Resolution order buildout extends chain was wrong. Also documented the
  resolution order and included in own builodut a small example.
  [jensens]

- Fix: Formatter printed a newline to much after ``required by``.
  [jensens]

- Fix: Do not complain about missing track file.  If it is not there,
  the buildout is simply not using the buildout extension.  [maurits]

- Fix #13: Added missing ``zc.buildout`` requirement.  [maurits]


1.1.1 (2016-01-20)
------------------

- Fix: Orphan detection failed when no tracking file was present.
  [jensens]

- Fix: Exception raised when no tracking file was present.
  [jensens]

- Fix: Color of requirements was not set explicitly.
  [jensens]


1.1 (2016-01-19)
----------------

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


1.0 (2016-01-13)
----------------

- Initial work.
  [jensens]
