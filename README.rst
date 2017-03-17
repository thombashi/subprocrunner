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

Execute a command
----------------------------

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

.. code::

    command: echo test
    return code: 0
    stdout: test

    command: ls __not_exist_dir__
    return code: 2
    stderr: ls: cannot access '__not_exist_dir__': No such file or directory


Get command history
----------------------------

.. code:: python

    from subprocrunner import SubprocessRunner

    SubprocessRunner.clear_history()
    SubprocessRunner.is_save_history = True

    SubprocessRunner("echo hoge").run()
    SubprocessRunner("echo foo").run()

    print("\n".join(SubprocessRunner.get_history()))

.. code::

    echo hoge
    echo foo


Installation
============

::

    pip install subprocrunner


Dependencies
============

Python 2.7+ or 3.3+

- `logbook <http://logbook.readthedocs.io/en/stable/>`__
- `mbstrdecoder <https://github.com/thombashi/mbstrdecoder>`__
- `typepy <https://github.com/thombashi/typepy>`__
- `six <https://pypi.python.org/pypi/six/>`__


Test dependencies
-----------------

- `pytest <http://pytest.org/latest/>`__
- `pytest-runner <https://pypi.python.org/pypi/pytest-runner>`__
- `tox <https://testrun.org/tox/latest/>`__
