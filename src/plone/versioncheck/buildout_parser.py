
# flake8: NOQA: E501

# from zc.buildout.buildout import HistoryItem
# from zc.buildout.buildout import SectionKey
from zc.buildout.buildout import Buildout

import os.path


def parse_buildout(buildout_filename):
    """Parse a buildout config."""
    if os.path.isfile(buildout_filename):
        buildout_config = Buildout(buildout_filename,
                                   [('buildout', 'verbosity', '10')])

        versions_section = buildout_config.get('buildout').get('versions')
        versionannotations_sections = buildout_config.get('buildout').get('versionannotations', 'versionannotations')

        for pkg_name, pkg_info in buildout_config._annotated.get(versions_section).items():
            print(pkg_name + ': ' + str(pkg_info.history))

        constrains = []
        for key, value in buildout_config.versions.items():
            if value[0] in ['=', '>', '<']:
                constrains.append(key + value)
            else:
                constrains.append(key + '==' + value)
        constrains = '\n'.join(constrains)
        print(constrains)

        version_annotations = buildout_config.get(versionannotations_sections)
        for annotation in version_annotations:
            print(annotation)
