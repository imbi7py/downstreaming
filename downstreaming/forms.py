# -*- coding: utf-8 -*-

'''
Forms used in the web interface
'''

from __future__ import absolute_import, unicode_literals, print_function

import re

import flask
from flask_wtf import Form
from wtforms import (BooleanField, StringField, TextAreaField, validators)

from .lib.models import Project


def strip(s):
    if s:
        return s.strip()
    else:
        return ""

def existing_project(_form, field):
    if flask.g.db.query(Project).filter_by(name=field.data).count() != 0:
        raise validators.ValidationError("Project already exists.")

PROJECT_NAME_RE = re.compile(r'^[\w_.-]+$')
def project_naming_format(_form, field):
    if not PROJECT_NAME_RE.match(field.data):
        raise validators.ValidationError(
            "Only letters, numbers, dots, dashes and underscores are allowed "
            "in the project name.")

class ListMinLength(object):
    def __init__(self, minlength):
        self.minlength = int(minlength)
    def __call__(self, form, field):
        if len(field.data) < self.minlength:
            raise validators.ValidationError(
                "You must choose at least %d of them." % self.minlength)


class NewProject(Form):
    name = StringField("Name",
                       filters = [strip],
                       validators = [
                           validators.InputRequired(),
                           validators.Length(max=128),
                           existing_project,
                           project_naming_format
                       ])
    summary = StringField("Summary",
                          filters = [strip],
                          validators = [
                              validators.InputRequired(),
                              validators.Length(max=255)
                          ])
    description = TextAreaField("Description",
                                filters = [strip],
                                validators=[validators.InputRequired()]
                               )

class NewReview(Form):
    reason = StringField("Reason",
                          filters = [strip],
                          validators = [validators.InputRequired()])

class EndReview(Form):
    approved = BooleanField("Approved", default=False)
