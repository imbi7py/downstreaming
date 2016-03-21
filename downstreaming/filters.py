# -*- coding: utf-8 -*-
'''
Custom template filters for the application
'''

from __future__ import absolute_import, unicode_literals, print_function
import arrow
from . import APP

@APP.template_filter('humanize')
def humanize_date(date):
    """ Template filter providing a more reader friendly date representation.
    """
    return arrow.get(date).humanize()

@APP.template_filter('review_result')
def review_result(approved):
    """ Template filter displaying a review outcome
    """
    return "approved" if approved else "rejected"
