# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '1.2.2.dev0'

long_description = '{0}\n\n{1}'.format(
    open('README.rst').read(),
    open('CHANGES.rst').read()
)

setup(
    name='plone.versioncheck',
    version=version,
    description='Checks pinned versions with overrides in a cascaded buildout',
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        'Framework :: Buildout',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='plone buildout version ',
    author='Jens W. Klein',
    author_email='jens@bluedynamics.com',
    url='https://github.com/plone/plone.versioncheck',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['plone', ],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'CacheControl[filecache]',
        'colorama',
        'jinja2',
        'requests',
        'setuptools>=12',
        'zc.buildout',
    ],
    setup_requires=[
        'setuptools>=12'
    ],
    entry_points={
        'console_scripts': [
            'versioncheck = plone.versioncheck.script:run',
        ],
        'zc.buildout.extension': [
            'default = plone.versioncheck.tracking:install',
        ]
    },
    test_suite='plone.versioncheck.tests',
)
