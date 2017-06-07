plone.versioncheck Parser
=========================

As plone.versioncheck analyze Python and Plone Projects a Parser is the base for this work.
plone.versioncheck should support following Projects types:

* Buildout (zc.buildout) - most Zope/Plone projects support that
* Python Projects depending on requirements.txt and optional constrains.txt
* Python Packages based on setup.py (install_requires, setup_requires, extras_requires)

plone.versioncheck 1.x Series only supports Buildout and use an own parser to extract information from the buildout files.
zc.buildout is a very powerful tool to assembly and deploy Project Setups.
As it needs to analyze and parse it configuration files it also has a very powerful parser and annotater, which might not be very good documented, but be usefull for this project.

zc.buildout API
---------------

.. testcode::

    from zc.buildout.buildout import Buildout
    from zc.buildout.buildout import HistoryItem
    from zc.buildout.buildout import SectionKey

    buildout_config = Buildout('buildout.cfg',
                               [('buildout', 'verbosity', '10')])

    versions_section = buildout_config.get('buildout').get('versions')
    versionannotations_sections = buildout_config.get('buildout') \
                                  .get('versionannotations',
                                       'versionannotations')

    for pkg_name, pkg_info in buildout_config._annotated \
                              .get(versions_section).items():
        print(pkg_name + ': ' + str(pkg_info.history))

    constrains = []
    for key, value in buildout_config.versions.items():
        if value[0] in ['=', '>', '<']:
            constrains.append(key + value)
        else:
            constrains.append(key + '==' + value)
    constrains = '\n'.join(constrains)
    print(constrains)

.. testoutput::
  :hide:
  :options: +NORMALIZE_WHITESPACE

  ...

.. no valid testoutput providable, as order of a directory is not guaranteed.


Core Elements of zc.buildout are those three classes:

* Buildout
* SectionKey
* HistoryItem
