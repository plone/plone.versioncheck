# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = "1.8.0"

long_description = "{0}\n\n{1}".format(
    open("README.rst").read(), open("CHANGES.rst").read()
)

setup(
    name="plone.versioncheck",
    version=version,
    description="Checks pinned versions with overrides in a cascaded buildout",
    long_description=long_description,
    # Get more strings from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Buildout :: Extension",
        "Framework :: Buildout :: Recipe",
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Quality Assurance",
    ],
    keywords="plone buildout version ",
    author="Jens W. Klein",
    author_email="jens@bluedynamics.com",
    url="https://github.com/plone/plone.versioncheck",
    license="GPL version 2",
    packages=find_packages("src"),
    namespace_packages=["plone"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "CacheControl[filecache]",
        "colorama",
        "jinja2",
        "requests",
        "setuptools>=12",
        "zc.buildout",
    ],
    setup_requires=["setuptools>=12"],
    extras_require={
        "docs": ["Sphinx"],
        "release": ["zest.releaser"],
        "test": ["pytest", "responses"],
        "develop": ["pdbpp", "isort"],
    },
    entry_points={
        "console_scripts": ["versioncheck = plone.versioncheck.script:run"],
        "zc.buildout.extension": ["default = plone.versioncheck.tracking:install"],
    },
)
