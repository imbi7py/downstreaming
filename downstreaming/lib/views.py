# -*- coding: utf-8 -*-

'''
Views that don't rely specifically on the use of Flask

Exceptions:

- We use the Form subclass coming from Flask-WTF, which transparently uses
  Flask's request and session proxies. However, we don't use the special API
  methods here (like validate_on_submit() or hidden_tag()), so it should be
  easy to switch to a vanilla WTForm, we'd only have to re-implement the
  session-based CSRF token generation and validation.
'''

from __future__ import absolute_import, unicode_literals, print_function

import os
import json
from time import time

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from .. import forms
from .models import Project, Review, Reviewer, Comment
from .utils import Result


def index(db):
    recent_projects = db.query(Project).filter(Project.active
        ).order_by(Project.submitted.desc()).limit(10).all()
    updated_revs = db.query(Review).join(Comment
        ).order_by(Comment.date.desc()).limit(10).all()
    projects_without_rev = db.query(Project).filter(
        Project.active, ~Project.reviews.any()
        ).order_by(Project.submitted.desc()).limit(10).all()
    return Result({"recent_projects": recent_projects,
                   "updated_revs": updated_revs,
                   "projects_without_rev": projects_without_rev,
                   })


def projects(db):
    projects = db.query(Project).filter(Project.active).all()
    projects.sort(key=lambda p: p.last_review_activity)
    return Result({"projects": projects})


def project(db, name):
    try:
        project = db.query(Project).filter_by(name=name).one()
    except NoResultFound:
        return Result({"message": "Unknown project: {}".format(name)},
                      code=404)
    else:
        return Result({"project": project})


def newproject(db, method, data, username):
    form = forms.NewProject(data)
    result = Result({"form": form})
    if method == "POST" and form.validate():
        project = Project(
            name=form.name.data,
            summary=form.summary.data,
            description=form.description.data,
            owner=username,
            )
        db.add(project)
        try:
            db.commit()
        except SQLAlchemyError:
            result.flash.append(("An error occurred while adding your "
                "project, please contact an administrator.", "danger"))
        else:
            result.flash.append(("Project successfully created!", "success"))
            result.redirect = ('project', {"name": project.name})

    return result


def user_projects(db, username):
    all_projects = db.query(Project).filter_by(owner=username).all()
    all_projects.sort(key=lambda p: p.last_review_activity)
    projects = []
    old_projects = []
    for project in all_projects:
        if project.active:
            projects.append(project)
        else:
            old_projects.append(project)
    return Result({"projects": projects, "old_projects": old_projects})


def user_reviews(db, username):
    reviews = db.query(Review).join(Reviewer).filter(
            Reviewer.reviewer_name == username
        ).order_by(Review.date_start).all()
    return Result({"reviews": reviews})
