# -*- coding: utf-8 -*-

"""
Framework-independant wrappers.

Those functions are proxies for the framework's functions.
"""

from __future__ import absolute_import, unicode_literals, print_function

class Result:
    def __init__(self, context=None, code=200):
        self.context = context or {}
        self.flash = []
        # `redirect` must be None or a tuple: (view_name, view_kwargs)
        self.redirect = None
        self.code = code
