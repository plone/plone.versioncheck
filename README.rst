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
      -p, --pypi            check pypi for newer versions
      --debug-limit DEBUG_LIMIT
                            Limit the number of pypi versions fetched for
                            debugging


Example display
---------------

Here w/o colors::

    $ plone.versioncheck/bin/versioncheck -pb coredev5/buildout.cfg

    Check Versions
    --------------
    accesscontrol........................ 3.0.11................ coredev5/versions.cfg
                                          2.13.13............... http://dist.plone.org/versions/zope-2-13-23-versions.cfg
                                          3.0.12................ bugfix (PyPI)
    acquisition.......................... 2.13.9................ http://dist.plone.org/versions/zope-2-13-23-versions.cfg
                                          4.2.2................. major (PyPI)
    archetypes.multilingual.............. 3.0.1................. coredev5/versions.cfg
    archetypes.referencebrowserwidget.... 2.5.6................. coredev5/versions.cfg
    archetypes.schemaextender............ 2.1.5................. coredev5/versions.cfg
    argcomplete.......................... 0.8.3................. coredev5/tests.cfg
                                          1.0.0................. major (PyPI)
                                          0.9.0................. minor (PyPI)
                                          0.8.9................. bugfix (PyPI)
    argh................................. 0.25.0................ coredev5/tests.cfg
                                          0.26.1................ minor (PyPI)

    [... skipped a bunch ...]

                                          0.16.................. minor (PyPI)
    collective.recipe.sphinxbuilder...... 0.7.1................. coredev5/tests.cfg
                                          0.8.2................. minor (PyPI)
                                          0.7.4................. bugfix (PyPI)
    collective.recipe.template........... 1.9................... coredev5/versions.cfg
                                          1.13.................. minor (PyPI)
    collective.xmltestreport............. 1.3.3................. coredev5/versions.cfg
    collective.z3cform.datagridfield..... 1.1................... coredev5/versions.cfg
    collective.z3cform.datagridfield-demo 0.5................... coredev5/versions.cfg
                                          0.6................... minor (PyPI)
    collective.z3cform.datetimewidget.... 1.2.7................. coredev5/versions.cfg
    colorama............................. 0.3.3................. coredev5/tests.cfg
                                          0.3.6................. bugfix (PyPI)
    configparser......................... 3.5.0b2............... coredev5/tests.cfg
    coverage............................. 3.5.2................. http://dist.plone.org/versions/zopetoolkit-1-0-8-ztk-versions.cfg
                                          4.0.3................. major (PyPI)
                                          3.7.1................. minor (PyPI)
                                          3.5.3................. bugfix (PyPI)
                                          4.1b1................. majorpre (PyPI)

    [... skipped a bunch ...]

    zope.testing......................... 3.9.7................. http://dist.plone.org/versions/zopetoolkit-1-0-8-ztk-versions.cfg
                                          4.5.0................. major (PyPI)
                                          3.10.3................ minor (PyPI)
    zope.testrunner...................... 4.4.4................. coredev5/versions.cfg
                                          4.4.9................. bugfix (PyPI)
    zope.thread.......................... 3.4................... http://dist.plone.org/versions/zopetoolkit-1-0-8-zopeapp-versions.cfg
    zope.traversing...................... 3.13.2................ http://dist.plone.org/versions/zopetoolkit-1-0-8-ztk-versions.cfg
                                          4.0.0................. major (PyPI)
                                          3.14.0................ minor (PyPI)
    zope.viewlet......................... 3.7.2................. http://dist.plone.org/versions/zopetoolkit-1-0-8-ztk-versions.cfg
                                          4.0.0................. major (PyPI)
    zope.xmlpickle....................... 3.4.0................. http://dist.plone.org/versions/zopetoolkit-1-0-8-zopeapp-versions.cfg
                                          3.5.0dev.............. minorpre (PyPI)
    zope2................................ 2.13.23............... http://dist.plone.org/versions/zope-2-13-23-versions.cfg
    zopeundo............................. 2.12.0................ http://dist.plone.org/versions/zope-2-13-23-versions.cfg
                                          4.0................... major (PyPI)


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

