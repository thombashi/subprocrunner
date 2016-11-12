subprocrunner
=============

.. image:: https://badge.fury.io/py/subprocrunner.svg
    :target: https://badge.fury.io/py/subprocrunner

.. image:: https://img.shields.io/pypi/pyversions/subprocrunner.svg
   :target: https://pypi.python.org/pypi/subprocrunner

.. image:: https://img.shields.io/travis/thombashi/subprocrunner/master.svg?label=Linux
    :target: https://travis-ci.org/thombashi/subprocrunner

.. image:: https://img.shields.io/appveyor/ci/thombashi/subprocrunner/master.svg?label=Windows
    :target: https://ci.appveyor.com/project/thombashi/subprocrunner/branch/master

.. image:: https://coveralls.io/repos/github/thombashi/subprocrunner/badge.svg?branch=master
    :target: https://coveralls.io/github/thombashi/subprocrunner?branch=master


Summary
-------

A python library of subprocess module wrapper.


Examples
========

.. code:: python

    from subprocrunner import SubprocessRunner

    runner = SubprocessRunner("echo test")
    print("return code: {:d}".format(runner.run()))
    print("stdout: {}".format(runner.stdout))

.. code::

    return code: 0
    stdout: test

Installation
============

::

    pip install subprocrunner


Dependencies
============

Python 2.7+ or 3.3+

- `DataPropery <https://github.com/thombashi/DataProperty>`__
- `six <https://pypi.python.org/pypi/six/>`__


Test dependencies
-----------------

- `pytest <http://pytest.org/latest/>`__
- `pytest-runner <https://pypi.python.org/pypi/pytest-runner>`__
- `tox <https://testrun.org/tox/latest/>`__
