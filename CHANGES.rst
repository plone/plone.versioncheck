Changelog
=========

1.5.2 (unreleased)
------------------

- Fix an ``IndexError: string index out of range`` error with empty states in the formatter.
  [thet]

- Added basic tests to package.
  [loechel]

1.5.1 (2017-01-23)
------------------

- Fix Version Compare.
  [loechel]

1.5.0 (2016-10-15)
------------------

- Use code analysis for QA (and fix issues with pep8 et al.)
  [jensens]

- Fix Manifest (jinja file was missing).
  [jensens]

- Implement #25: Annotate versions used.
  [jensens]


1.4 (2016-09-30)
----------------

- New option '-N': feature to hide orphaned without updates.
  This reduces the noise in a environment where orphaned are used by intend.
  [jensens]


1.3 (2016-05-19)
----------------

- Add .editorconfig File to maintain code convetions following Plone API
  [loechel]

- Add Support for Python 3
  [loechel]

- Fix various documentation typos.
  [jean]

1.2.1 (2016-01-26)
------------------

- Cache buildout cfg files fetched over the network.
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
