Dependency Tracking
===================

One core element of plone.versioncheck is to keep track of all necessary dependencies for a project or product.

Since buildout (zc.buildout) is / was the primary scope of this project, that might be a bit more complicated than for pip installable projects / products.

With ``pip`` you have those commands:

.. code:: sh

    pip install -r requirements.txt - c constrains.txt

    pip freeze

that will keep track of all required packages and versions.

Python packages ``setup.py`` did have special params:

* ``install_requires``
* ``setup_requires``
* ``extras_require``

While ``install_requires`` and ``setup_requires`` are lists of Packages with possible Version Annotations ``extras_require`` is a dictionary with Names and a list on Packages.

Buildout and Packages Extras are special in comparison to a pip project.
Extras did define additional package dependencies necessary to do specific actions (like building docs, make a release) or to provide additional functionallity.
Buildout manages larger installations and configures applications.

While a Python project or a Python Package could only have one specific version set at runtime, a Buildout project could theoretically have more than one version for the same python package as a dependency for different sections and build scripts.

Today Buildout is normally used in combination with ``virtualenv``.


Setuptools Tracking
-------------------

The Python Setuptools are a core dependency of almost all Python packages and a essential part of all ``virtualenv`` 's.

Within the Setuptools Package the ``pkg_resources`` modul is defined that
