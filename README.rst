.. contents:: **subprocrunner**
   :backlinks: top
   :depth: 2


Summary
=============
A Python wrapper library for subprocess module.


.. image:: https://badge.fury.io/py/subprocrunner.svg
    :target: https://badge.fury.io/py/subprocrunner
    :alt: PyPI package version

.. image:: https://img.shields.io/pypi/pyversions/subprocrunner.svg
    :target: https://pypi.org/project/subprocrunner
    :alt: Supported Python versions

.. image:: https://img.shields.io/travis/thombashi/subprocrunner/master.svg?label=Linux/macOS%20CI
    :target: https://travis-ci.org/thombashi/subprocrunner
    :alt: Linux/macOS CI status

.. image:: https://img.shields.io/appveyor/ci/thombashi/subprocrunner/master.svg?label=Windows%20CI
    :target: https://ci.appveyor.com/project/thombashi/subprocrunner/branch/master
    :alt: Windows CI status

.. image:: https://coveralls.io/repos/github/thombashi/subprocrunner/badge.svg?branch=master
    :target: https://coveralls.io/github/thombashi/subprocrunner?branch=master
    :alt: Test coverage


Examples
========
Execute a command
----------------------------
:Sample Code:
    .. code:: python

        from subprocrunner import SubprocessRunner

        runner = SubprocessRunner("echo test")
        print("command: {:s}".format(runner.command))
        print("return code: {:d}".format(runner.run()))
        print("stdout: {:s}".format(runner.stdout))

        runner = SubprocessRunner("ls __not_exist_dir__")
        print("command: {:s}".format(runner.command))
        print("return code: {:d}".format(runner.run()))
        print("stderr: {:s}".format(runner.stderr))

:Output:
    .. code::

        command: echo test
        return code: 0
        stdout: test

        command: ls __not_exist_dir__
        return code: 2
        stderr: ls: cannot access '__not_exist_dir__': No such file or directory

dry run
----------------------------
:Sample Code:
    .. code:: python

        from subprocrunner import SubprocessRunner

        runner = SubprocessRunner("echo test", dry_run=True)
        print("command: {:s}".format(runner.command))
        print("return code: {:d}".format(runner.run()))
        print("stdout: {:s}".format(runner.stdout))

:Output:
    .. code::

        command: echo test
        return code: 0
        stdout:

Get execution command history
--------------------------------------------------------
:Sample Code:
    .. code:: python

        from subprocrunner import SubprocessRunner

        SubprocessRunner.clear_history()
        SubprocessRunner.is_save_history = True

        SubprocessRunner("echo hoge").run()
        SubprocessRunner("echo foo").run()

        print("\n".join(SubprocessRunner.get_history()))

:Output:
    .. code::

        echo hoge
        echo foo

Get a command information
----------------------------
.. code-block:: pycon

    >>> from subprocrunner import Which
    >>> which = Which("ls")
    >>> which.is_exist()
    True
    >>> which.abspath()
    '/usr/bin/ls'
    >>> which
    command=ls, is_exist=True, abspath=/usr/bin/ls


Installation
============

Install from PyPI
------------------------------
::

    pip install subprocrunner

Install from PPA (for Ubuntu)
------------------------------
::

    sudo add-apt-repository ppa:thombashi/ppa
    sudo apt update
    sudo apt install python3-subprocrunner


Dependencies
============
Python 2.7+ or 3.4+

- `mbstrdecoder <https://github.com/thombashi/mbstrdecoder>`__

Optional dependencies
----------------------------------
- `logbook <https://logbook.readthedocs.io/en/stable/>`__
    - Logging using logbook if the package installed

Test dependencies
-----------------
- `pytest <https://docs.pytest.org/en/latest/>`__
- `pytest-runner <https://github.com/pytest-dev/pytest-runner>`__
- `six <https://pypi.org/project/six/>`__
- `tox <https://testrun.org/tox/latest/>`__
- `typepy <https://github.com/thombashi/typepy>`__
