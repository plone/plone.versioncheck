Changelog
=========



1.2.2 (unreleased)
------------------

New:

  - Add .editorconfig File to maintain code conventions following Plone API
  - Add Support for Python 3
  - Basic test support (via ./bin/py setup.py test)

Fix:

  - handle extends in parent folder (initial work to fix #20)
    [ale-rt]


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
