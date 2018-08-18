# encoding: utf-8

"""
source code from six: https://github.com/benjaminp/six/blob/master/LICENSE
"""

from __future__ import absolute_import

import sys


# Useful for very coarse version differentiation.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


if PY3:
    text_type = str
else:
    text_type = unicode
