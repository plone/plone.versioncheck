Caching
=======

plone.versioncheck should also check for newer avalibale versions.
Therefore plone.versioncheck needs to communicate with the Python Package Index (PyPI).

Every network communication is expensive, and asking PyPI for each package and each version of those packages for data could result in several hundreds of PyPI calls.
Even if the Package Index istself provides a JSON API for that and should be able to handle several hundreds of request per second, this could be assumed unnecessary or even an denial of service attack against PyPI, caused by stupiness.

Necessary PyPI data for a specific version should not change over lifetime of PyPI, a package should only get additional new versions.

If we conclude, that PyPI data could be easily persistent and don't need to be updated on each run of plone.versioncheck we could work with a global pypi cache file.

plone.versioncheck did used Request caching (via CacheControl), we do change that to a simple file in the home directory of the executing user.
Our cache file would be a simple json file (.versioncheck.json) that stores all necessary Information to a version:

* ``version`` --> Version String
* ``release_date`` --> Release Data
* ``classifiers`` --> Supported Python / Plone Versions and Platform, ...

Example:

.. code:: JSON

    {
      "setuptools": {
        "34.0.0": {
          "release_date": "2017-01-23",
          "classifiers": [
            "Development Status :: 5 - Production/Stable"
            "Intended Audience :: Developers"
            "License :: OSI Approved :: MIT License"
            "Operating System :: OS Independent"
            "Programming Language :: Python :: 2"
            "Programming Language :: Python :: 2.6"
            "Programming Language :: Python :: 2.7"
            "Programming Language :: Python :: 3"
            "Programming Language :: Python :: 3.3"
            "Programming Language :: Python :: 3.4"
            "Programming Language :: Python :: 3.5"
            "Programming Language :: Python :: 3.6"
            "Topic :: Software Develop…raries :: Python Modules"
            "Topic :: System :: Archiving :: Packaging"
            "Topic :: System :: Systems Administration"
            "Topic :: Utilities"
          ]
        },
        "12.0": {
          "release_date": "2015-01-16",
          "classifiers": [
            "Development Status :: 5 - Production/Stable"
            "Intended Audience :: Developers"
            "License :: OSI Approved :…tware Foundation License"
            "License :: OSI Approved :: Zope Public License"
            "Operating System :: OS Independent"
            "Programming Language :: Python :: 2.6"
            "Programming Language :: Python :: 2.7"
            "Programming Language :: Python :: 3"
            "Programming Language :: Python :: 3.1"
            "Programming Language :: Python :: 3.2"
            "Programming Language :: Python :: 3.3"
            "Programming Language :: Python :: 3.4"
            "Topic :: Software Develop…raries :: Python Modules"
            "Topic :: System :: Archiving :: Packaging"
            "Topic :: System :: Systems Administration"
            "Topic :: Utilities"
          ]
        }
      }
    }

As such a file might grow, it is pure text data, it will roughly become several MB large.
