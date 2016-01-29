.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide_addons.html
   This text does not appear on pypi or github. It is a comment.


=============================================================================
Checks pinned versions with overrides in a cascaded buildout
=============================================================================

**plone.versioncheck**

.. contents::

Features
========

1) **Checks buildouts ``[versions]`` sections** while stepping through the cascaded ``extends``

   - command line script collects the inherited version pins, remembers where a version pin comes from.
   - It displays the result in order to enable a human to check that pins and overrides are OK.
   - Output is colored; this helps to identify packages which have newer versions available.
   - Machine readable output as JSON on demand.

2) **Checks Python Package Index (PyPI)** for newer versions.

   - Detects if a newer major, minor or bugfix (or a prerelease) is available.

3) **Buildout extension** records the **current versions state** and **requirements**

   - versions state and requirements are written to a file,
   - versions from the file will be consumed by the command line tool
       - orphaned version pins are detected,
       - it shows which package pulled in another package as dependency.

It works best with `semantically <http://semver.org/>`_ and only with `syntactically <https://pythonhosted.org/setuptools/setuptools.html#specifying-your-project-s-version>`_ correct version numbers!

Usage
=====

Install with your buildout
--------------------------

Add a section to install it as a script and add it as an extension to your builodut::

    [buildout]
    ...
    extensions =
        plone.versioncheck

    parts =
        ...
        ploneversioncheck
        ...

    ...

    [ploneversioncheck]
    recipe = zc.recipe.egg
    eggs = plone.versioncheck

    ...


Run buildout as usual.

Now a file ``.plone.versioncheck.tracked.json`` was generated in the buildout-directory.

This file will be used by ``bin/versioncheck`` to figure out which packages were finally used.

Run buildout again to regenerate this file.


commandline
-----------

::

    usage: versioncheck [-h] [-p] [-n] [-r] [-i] [-m] [--no-cache] [-b]
                        [--no-colors] [--debug-limit DEBUG_LIMIT]
                        [buildout]

    Fetch information about pinned versions and its overrides in simple and complex/cascaded buildouts.

    positional arguments:
      buildout              path to buildout.cfg or other *.cfg file

    optional arguments:
      -h, --help            show this help message and exit
      -p, --pypi            check pypi for newer versions
      -n, --newer           display only packages with newer version than active
      -r, --required-by     show information about requirements (only if tracking
                            file is available)
      -i, --ignore-tracking
                            ignore tracking file (if present)
      -m, --machine         show as machine readable output (json)
      --no-cache            do not use a cache for pypi
      -b, --browser         show as html for webbrowser
      --no-colors           do not show colors
      --debug-limit DEBUG_LIMIT
                            Limit the number of pypi versions fetched for
                            debugging

    [...]


Files created
-------------

If the script was used with the ``--pypi`` option, a directory ``.plone.versioncheck.cache`` will be created.
It contains the cache of the requests to PyPI or external buildout configuration files.
To clear the cache, remove the directory.
The caching library uses the expiration headers of the response from PyPI, so even with cache it starts fetching new records.

If the extension was used, a file ``.plone.versioncheck.tracked.json`` will be created.
It contains the information from last buildout run.


Output explained
================

Legend of states and colors
---------------------------

[D]evelopment Egg
    A development egg is usually active.
    Description shows location.
    Color: Green

[A]ctive Pin
     Pinned version. Package is used and recent, all seems fine.
     Color: White

[I]nherited Pin
     Unused pin. If older than active, the pin color is gray; if newer, it is yellow.

[O]rphaned
    If tracked, it shows whether the package in the given configuration was used at all.
    Be careful with this information!
    I.e. in a development buildout file, other packages are used than in a live or continuous integration buildout!
    Color: Magenta

[X] Unpinnend
    Tracked, but no pin in ``[versions]`` sections were found.
    Color: Red

[U]pdate final release
    At PyPI there is a newer final version available (major, minor or bugfix).
    Descriptions shows on which level.
    Color: Cyan

[P]rerelease update
    At PyPI there is a newer prerelease version available (major, minor or bugfix).
    Descriptions shows on which level.
    Only if there is no final release update available.
    Color: Blue

[R] Required by
    If tracked and option ``--required-by`` was given, show packages this package is required by.
    Valid for current active/used version.
    Keep in mind this is based on the declared requirements, missing or implicit requirements are not covered.


Order of versions
-----------------

Order of versions is the buildout resolution order (how they are resolved by buildout in the extends chain/tree).
After that, the PyPI releases are shown (major, minor, pre, then the prereleases)

Example, given in each a version of ``my.pkg`` was declared:

1. ``buildout.cfg`` with ``my.pkg=3.0.3``

    1. ``buildout.cfg`` extends ``foo.cfg`` with ``my.pkg=3.0.1``
    2. ``buildout.cfg`` extends ``bar.cfg`` with ``my.pkg=2.0``

       2. ``foo cfg`` extends ``baz.cfg`` with ``my.pkg=3.1``

2. found a newer versions at pypi

    1. major ``my.pkg=4.0``
    2. minor ``my.pkg=3.2``
    3. major ``prerelease my.pkg=5.1b2``

Output looks like so::

    my.pkg
        3.0.3............... A buildout.cfg
        2.0 ................ I bar.cfg
        3.0.1 .............. I foo.cfg
        3.1 ................ I baz.cfg
        4.0 ................ U Major
        3.2 ................ U Minor
        5.1b2............... P Majorpre



Example
-------

Here w/o colors, run on ``buildout.coredev``::

    $ ./bin/versioncheck -p buildout.cfg

    accesscontrol
        3.0.12 .... A versions.cfg
        2.13.13 ... I http://dist.plone.org/versions/zope-2-13-23-versions.cfg
    acquisition
        4.2.2 ..... A versions.cfg
        2.13.9 .... I http://dist.plone.org/versions/zope-2-13-23-versions.cfg
    alabaster
        0.7.7 ..... X unpinned
    archetypes.multilingual
        3.0.1 ..... A versions.cfg
    archetypes.referencebrowserwidget
        2.5.6 ..... A versions.cfg
    archetypes.schemaextender
        2.1.5 ..... A versions.cfg
    argcomplete
        1.0.0 ..... A tests.cfg
    argh
        0.26.1 .... A tests.cfg
    argparse
        (unset) ... A versions.cfg
        1.1 ....... I http://dist.plone.org/versions/zopetoolkit-1-0-8-ztk-versions.cfg
        Can not check legacy version number.  U Error
    autopep8
        1.2.1 ..... A tests.cfg

    [... skipped a bunch ...]

    coverage
        3.7.1 ..... A tests.cfg
        3.5.2 ..... I http://dist.plone.org/versions/zopetoolkit-1-0-8-ztk-versions.cfg
        4.0.3 ..... U Major
        4.1b1 ..... P Majorpre
    cssmin
        0.2.0 ..... A versions.cfg
    cssselect
        0.9.1 ..... A versions.cfg
    datetime
        3.0.3 ..... A versions.cfg
        2.12.8 .... I http://dist.plone.org/versions/zope-2-13-23-versions.cfg
        4.0.1 ..... U Major
    decorator
        4.0.6 ..... A versions.cfg

    [... skipped a bunch ...]

    plone.app.textfield
        1.2.6 ..... A versions.cfg
    plone.app.theming
        1.2.17.dev0  D /home/workspacejensens/coredev5/src/plone.app.theming/src
        1.2.16 .... I versions.cfg
    plone.app.tiles
        2.1.0 ..... A versions.cfg
        2.2.0 ..... U Minor

    [... skipped a bunch ...]

Source Code and Contributions
=============================

If you want to help with the development (improvement, update, bug-fixing, ...) of ``plone.versioncheck`` this is a great idea!

Please follow the `contribution guidelines <http://docs.plone.org/develop/coredev/docs/guidelines.html>`_.

- `Source code at Github <https://github.com/plone/plone.versioncheck>`_
- `Issue tracker at Github <https://github.com/plone/plone.versioncheck>`_

Maintainer of ``plone.versioncheck`` is Jens Klein.
We appreciate any contribution and if a release is needed to be done on PyPI, please just contact one of us.

Development
===========

There must be a ``python`` binary available in system path pointing to Python >=2.7.x
Clone the project. Then::

    $ bootstrap.sh

License
=======

The project is licensed under the GPLv2.

