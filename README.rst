.. contents:: **subprocrunner**
   :backlinks: top
   :depth: 2


Summary
=============
A Python wrapper library for ``subprocess`` module.

.. image:: https://badge.fury.io/py/subprocrunner.svg
    :target: https://badge.fury.io/py/subprocrunner
    :alt: PyPI package version

.. image:: https://img.shields.io/pypi/pyversions/subprocrunner.svg
    :target: https://pypi.org/project/subprocrunner
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/implementation/subprocrunner.svg
    :target: https://pypi.org/project/subprocrunner
    :alt: Supported Python implementations

.. image:: https://github.com/thombashi/subprocrunner/actions/workflows/lint_and_test.yml/badge.svg
    :target: https://github.com/thombashi/subprocrunner/actions/workflows/lint_and_test.yml
    :alt: CI status of Linux/macOS/Windows

.. image:: https://coveralls.io/repos/github/thombashi/subprocrunner/badge.svg?branch=master
    :target: https://coveralls.io/github/thombashi/subprocrunner?branch=master
    :alt: Test coverage


Usage
========
Execute a command
----------------------------
:Sample Code:
    .. code:: python

        from subprocrunner import SubprocessRunner

        runner = SubprocessRunner(["echo", "test"])
        print(runner)
        print(f"return code: {runner.run()}")
        print(f"stdout: {runner.stdout}")
        
        runner = SubprocessRunner(["ls", "__not_exist_dir__"])
        print(runner)
        print(f"return code: {runner.run()}")
        print(f"stderr: {runner.stderr}")
        
:Output:
    .. code::

        SubprocessRunner(command='echo test', returncode='not yet executed')
        return code: 0
        stdout: test
        
        SubprocessRunner(command='ls __not_exist_dir__', returncode='not yet executed')
        return code: 2
        stderr: ls: cannot access '__not_exist_dir__': No such file or directory

Execute a command with retry
--------------------------------------------------------

:Sample Code:
    .. code:: python

        from subprocrunner import Retry, SubprocessRunner

        SubprocessRunner(command).run(retry=Retry(total=3, backoff_factor=0.2, jitter=0.2))

Raise an exception when a command execution failed
--------------------------------------------------------
:Sample Code:
    .. code:: python

        import sys
        from subprocrunner import SubprocessRunner
        from subprocrunner.error import CalledProcessError

        runner = SubprocessRunner("ls not-exist-dir")

        # raise an exception at run
        try:
            runner.run(check=True)
        except CalledProcessError as e:
            print(f"run(check=True): {e}\n{e.stderr}", file=sys.stderr)


        # raise an exception after run
        runner.run()
        try:
            runner.raise_for_returncode()
        except CalledProcessError as e:
            print(f"raise_for_returncode(): {e}\n{e.stderr}", file=sys.stderr)

:Output:
    .. code::

        run(check=True): Command 'ls not-exist-dir' returned non-zero exit status 2.
        ls: cannot access 'not-exist-dir': No such file or directory

        raise_for_returncode(): Command 'ls not-exist-dir' returned non-zero exit status 2.
        ls: cannot access 'not-exist-dir': No such file or directory

dry run
----------------------------
Commands are not actually run when passing ``dry_run=True`` to ``SubprocessRunner`` class constructor.

:Sample Code:
    .. code:: python

        from subprocrunner import SubprocessRunner

        runner = SubprocessRunner("echo test", dry_run=True)
        print(runner)
        print(f"return code: {runner.run()}")
        print(f"stdout: {runner.stdout}")
        
:Output:
    .. code::

        SubprocessRunner(command='echo test', returncode='not yet executed', dryrun=True)
        return code: 0
        stdout: 

Get execution command history
--------------------------------------------------------
:Sample Code:
    .. code:: python

        from subprocrunner import SubprocessRunner

        SubprocessRunner.clear_history()
        SubprocessRunner.is_save_history = True
        
        SubprocessRunner(["echo", "hoge"]).run()
        SubprocessRunner(["echo", "foo"]).run()
        
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
- Python 3.6+
- `Python package dependencies (automatically installed) <https://github.com/thombashi/subprocrunner/network/dependencies>`__

Optional dependencies
----------------------------------
- `loguru <https://github.com/Delgan/loguru>`__
    - Used for logging if the package installed
