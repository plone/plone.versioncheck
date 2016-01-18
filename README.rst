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

::

    usage: versioncheck [-h] [-b BUILDOUT] [-o] [-p] [--debug-limit DEBUG_LIMIT]

    Print info about pinned versions and its overrides

    optional arguments:
      -h, --help            show this help message and exit
      -b BUILDOUT, --buildout BUILDOUT
                            path to buildout.cfg or other cfg file
      -o, --overrides       display only packages with overrides
      -b BUILDOUT, --buildout BUILDOUT
                            path to .plone.versioncheck.tracked.json or other json file
      -o, --overrides       display only packages with overrides
      -p, --pypi            check pypi for newer versions
      --debug-limit DEBUG_LIMIT
                            Limit the number of pypi versions fetched for
                            debugging


Output explained
----------------

Legend:

``orphaned``
    If buildout extension generated file is given it shows if the package in the given configuration was used.
    Be careful with this information!
    I.e. in a development buildout file other packages are used than in a live or continious integration buildout!

``D``
    Development Egg, active.

``A``
    Active pinned version (active if not development egg).

``I``
    Inherited pin, unused.

``U``
    Update from PyPI is available.

``P``
    Prerelease update from PyPI is available.

``X``
    unpinned - tracked, but no pin in versions section was found


Colors of package name:

``white``
    Package is used and recent, all seems fine.

``green``
    Development package is used.

``cyan``
    A release update is available (major, minor or bugfix).

``yellow``
    Inherited package version number is greater than used.

``blue``
    A prerelease update is available, but no non-prerelease update.

``magenta``
    Package seems orphaned.

``red``
    Package is unpinnend.


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

