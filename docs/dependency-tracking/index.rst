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

Within the Setuptools Package the ``pkg_resources`` module is defined, that provides access to ``WorkingSet``, ``Requirements``, ``Distribution`` and ``Environment``.

Those ``WorkingSet`` allow it to retrieve informations for all installed Python packages in its context.
Precondition to have a ``WorkingSet`` / ``Environment`` is that the Project / Package is installed.

Buildout specifics
------------------

Buildout in the first place is older than virtualenv and should also do an isolation layer between the **System Python** and the application.
With later versions and better support of isolation via virtualenv and venv in Python 3 Buildout did focus on repeatable configuration generation and project deployments.
One core element persits, each generated Python script by Buildout just uses the in buildout defined interpreter (Python executable) and additional imports of eggs.

.. code:: Python
    :caption: "Example of plone.versioncheck itself"

    import sys
    sys.path[0:0] = [
       './plone.versioncheck/src',
       './plone.versioncheck/lib/python2.7/site-packages',
       '../buildout-cache/eggs/Jinja2-2.9.6-py2.7.egg',
       '../buildout-cache/eggs/CacheControl-0.12.2-py2.7.egg',
       '../buildout-cache/eggs/MarkupSafe-1.0-py2.7-macosx-10.12-x86_64.egg',
       '../buildout-cache/eggs/lockfile-0.12.2-py2.7.egg',
       '../buildout-cache/eggs/msgpack_python-0.4.8-py2.7-macosx-10.12-x86_64.egg',
      ]

This is a result, that each buildout section should be completely independen from each other.

It could go as far like:


.. code:: ini

    [buildout]

    executable = python3.4

    parts =
        demo1
        demo2

    [demo1]
    recipe = zc.recipe.egg:scripts
    interpreter = python2.7

    eggs =
        Sphinx==1.4.8
    scripts =
        sphinx-quickstart

    [demo2]
    recipe = zc.recipe.egg:scripts
    interpreter = python3.6

    eggs =
        Sphinx==1.6.2
    scripts =
        sphinx-build


Meaning a buildout could use several Python Versions as well as severale versions of the same package.

Tracking such a ``WorkingSet`` would be complicated and needs to be scoped.
It is even more complicated, as each Section could behave different based on the used recipe, if they even have a recipe.

Per definition each addressed section in buildout parts need to have a recipe.
The requirements for those recipes might not be reflected in the working set of the generated scripts.

Python versions dependencies
----------------------------

Some Python packages have different dependencies for different Python versions.

For Example a Python package that needs ``virtualenv`` and should work on Python 2 and Python 3 could import ``virtualenv`` for Python 2 but not for Python 3 as has become part of the standard library.
