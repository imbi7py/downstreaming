# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os

from datetime import timedelta

basedir = os.path.abspath(
    os.path.dirname(__file__)) # pylint: disable=invalid-name

# Set the time after which the session expires. Flask's default is 31 days.
# Default: ``timedelta(days=1)`` corresponds to 1 day.
PERMANENT_SESSION_LIFETIME = timedelta(days=1)


# url to the database server:
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
    basedir, '..', 'downstreaming.sqlite')


# secret key used to generate unique csrf token
SECRET_KEY = 'Change-me-Im-famous'

# If the authentication method is `fas`:
# To log in, the user must be a member of one of these groups
REQUIRED_GROUPS = ('packager', 'provenpackager')
# To get admin rights, the user must be a member of one of these groups
ADMIN_GROUPS = ('sysadmin-main', )
