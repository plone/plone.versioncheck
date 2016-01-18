.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide_addons.html
   This text does not appear on pypi or github. It is a comment.


=============================================================================
Checks pinned versions with overrides in a cascaded buildout
=============================================================================

**plone.versioncheck**

Features
--------

Command line script to check a buildouts ``[versions]`` section while stepping through the cascaded ``extends``.
The script collects the inherited version pins, remembers where a version pin comes from.
It displays then sorted result in order to enable a human to check pins and overrides are ok.

Optional Python Package Index (PyPI) may be checked for newer versions.
It works only with sematically korrekt version numbers.
If a newer major, minor or bugfix (or a prerelease) is available it will get printed.

Output is colored, this helps to identify packages which have newer versions available.

Usage
-----

Install with your buildout
~~~~~~~~~~~~~~~~~~~~~~~~~~

Add a section to install it as a script and add it as an extension to your builodut::

    [buildout]
    ...
    extensions =
        plone.versioncheck

    part =
        ...
        versioncheck
        ...

    ...

    [versioncheck]
    recipe = zc.recipe.egg
    eggs = plone.versioncheck

    ...


Run buildout as usal.

Now a file ``.plone.versioncheck.tracked.json`` was generated in the buildout-directory.

This file will be used by ``bin/versioncheck`` to figure out which packages were finally used.

Run buildout again to regenerate this file.


commandline
~~~~~~~~~~~

::

    usage: versioncheck [-h] [-p] [-n] [-r] [-i] [-m] [--no-colors]
                        [--debug-limit DEBUG_LIMIT]
                        [buildout]

    Fetch information about pinned versions and its overrides insimple and complex/cascaded buildouts.

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
      --no-colors           do not show colors
      --debug-limit DEBUG_LIMIT
                            Limit the number of pypi versions fetched for
                            debugging

    [...]


Output explained
----------------

Legend of states and colors:

``O``rphaned
    If buildout extension generated file is given it shows if the package in the given configuration was used.
    Be careful with this information!
    I.e. in a development buildout file other packages are used than in a live or continious integration buildout!
    Color: Magenta

``D``evelopmen Egg
    A development egg is usally active.
    Description show location.
    Color: Green


``A``ctive Pin
     Pinned version. Package is used and recent, all seems fine.
     Color: White

``I``nherited Pin
     unused pin. If older than active pin color is gray, if newer yellow.

``U``pdate final release
    At PyPI there is a newer final version available (major, minor or bugfix).
    Descriptions shows on which level.
    Color: Cyan

``P``rerelease update
    At PyPI there is a newer prerelease version available (major, minor or bugfix).
    Descriptions shows on which level.
    Only if there is no final release updatye available.
    Color: Blue

``X`` Unpinnend
    Tracked, but no pin in versions sections were found.
    Color: Red


Example (here w/o colors)::

    $ plone.versioncheck/bin/versioncheck -pb coredev5/buildout.cfg

    Check Versions
    --------------
    accesscontrol
        orphaned
        3.0.11 ................ P coredev5/versions.cfg
        2.13.13 ............... I http://dist.plone.org/versions/zope-2-13-23-versions.cfg
        3.0.12 ................ U Bugfix
    acquisition
        2.13.9 ................ P http://dist.plone.org/versions/zope-2-13-23-versions.cfg
        4.2.2 ................. U Major
    archetypes.multilingual
        3.0.1 ................. P coredev5/versions.cfg
    archetypes.referencebrowserwidget
        2.5.6 ................. P coredev5/versions.cfg
    archetypes.schemaextender
        2.1.5 ................. P coredev5/versions.cfg
    argcomplete
        0.8.3 ................. P coredev5/tests.cfg
        1.0.0 ................. U Major
        0.9.0 ................. U Minor
        0.8.9 ................. U Bugfix
    argh
        0.25.0 ................ P coredev5/tests.cfg
        0.26.1 ................ U Minor

    [... skipped a bunch ...]

    collective.recipe.sphinxbuilder
        0.7.1 ................. P coredev5/tests.cfg
        0.8.2 ................. U Minor
        0.7.4 ................. U Bugfix
    collective.recipe.template
        1.10a1.dev0 ........... D path/to/source
        1.9 ................... P coredev5/versions.cfg
        1.13 .................. U Minor


Source Code and Contributions
-----------------------------

If you want to help with the development (improvement, update, bug-fixing, ...) of ``plone.versioncheck`` this is a great idea!

Please follow the `contribution guidelines <http://docs.plone.org/develop/coredev/docs/guidelines.html>`_.

- `Source code at Github <https://github.com/plone/plone.versioncheck>`_
- `Issue tracker at Github <https://github.com/plone/plone.versioncheck>`_

Maintainer of plone.versioncheck is Jens Klein.
We appreciate any contribution and if a release is needed to be done on pypi, please just contact one of us.

Development
-----------

There must be a ``python`` binary available in system path pointing to Python >=2.7.x
Clone the project. Then::

    $ bootstrap.sh

License
-------

The project is licensed under the GPLv2.

