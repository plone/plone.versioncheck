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

Usage
-----

::

    usage: versioncheck [-h] [-b BUILDOUT] [-o]

    Print info about pinned versions and its overrides

    optional arguments:
     -h, --help            show this help message and exit
     -b BUILDOUT, --buildout BUILDOUT
                            path to buildout.cfg or other cfg file
     -o, --overrides       display only packages with overrides

Example display
---------------

::

    check versions
    --------------
    accesscontrol........................ 3.0.11................ coredev5/versions.cfg
                                          2.13.13............... http://dist.plone.org/versions/zope-2-13-23-versions.cfg
    acquisition.......................... 2.13.9................ http://dist.plone.org/versions/zope-2-13-23-versions.cfg
    archetypes.multilingual.............. 3.0.1................. coredev5/versions.cfg
    archetypes.referencebrowserwidget.... 2.5.6................. coredev5/versions.cfg
    archetypes.schemaextender............ 2.1.5................. coredev5/versions.cfg
    argcomplete.......................... 0.8.3................. coredev5/tests.cfg
    argh................................. 0.25.0................ coredev5/tests.cfg
    argparse............................. 1.1................... http://dist.plone.org/versions/zopetoolkit-1-0-8-ztk-versions.cfg
    autopep8............................. 0.9.7................. coredev5/tests.cfg
    ... and so on ...


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

There must be an ``python`` binary available in system path pointing to Python 2.7.
Also you need to have all installed to develop with Plone (see http://docs.plone.org/) then::

    $ bootstrap.sh

License
-------

The project is licensed under the GPLv2.

