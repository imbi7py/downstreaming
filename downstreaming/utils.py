# -*- coding: utf-8 -*-

"""
Some Flask-specific utility functions.
"""

from __future__ import absolute_import, unicode_literals, print_function

from six.moves import urllib_parse as urlparse

import flask
from six import string_types
from . import APP


def is_authenticated():
    """ Returns wether a user is authenticated or not.
    """
    return hasattr(flask.g, 'fas_user') and flask.g.fas_user is not None


def is_safe_url(target):
    """ Checks that the target url is safe and sending to the current
    website not some other malicious one.
    """
    ref_url = urlparse.urlparse(flask.request.host_url)
    test_url = urlparse.urlparse(
        urlparse.urljoin(flask.request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def is_service_admin(user):
    """ Is the user a service admin.
    """
    if not user:
        return False

    if not user.cla_done or len(user.groups) < 1:
        return False

    admins = APP.config['ADMIN_GROUP']
    if isinstance(admins, string_types):
        admins = [admins]
    admins = set(admins)

    return len(admins.intersection(set(user.groups))) > 0

def handle_result(result, template):
    for msg, style in result.flash:
        flask.flash(msg, style)
    if result.redirect:
        return flask.redirect(flask.url_for(
            result.redirect[0], **result.redirect[1]))
    if result.code != 200:
        result.context["code"] = result.code
        template = "error.html"
    return flask.render_template(template, **result.context), result.code
