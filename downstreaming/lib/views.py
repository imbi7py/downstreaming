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
from datetime import datetime

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

# Project display and registration

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

# Review display and registration

def _lookup_project(db, name):
    try:
        project = db.query(Project).filter_by(name=name).one()
    except NoResultFound:
        err_message = "Unknown project: {}".format(name)
        return None, Result({"message": err_message}, code=404)
    else:
        return project, None

def reviews(db, pname):
    project, err_result = _lookup_project(db, pname)
    if project is None:
        return err_result
    sql = db.query(Review).join(Project).order_by(Review.id.desc())
    print(sql)
    reviews = sql.all()
    print(reviews)
    return Result({"project": project, "reviews": reviews})

def review(db, method, data, pname, rid):
    print(pname, rid)
    project, err_result = _lookup_project(db, pname)
    if project is None:
        return err_result
    try:
        review = db.query(Review).join(Project).filter(Review.id==rid).one()
    except NoResultFound:
        err_message = "Unknown review ID for {}: {}".format(pname, rid)
        return Result({"message": err_message}, code=404)
    print(project.name, review.id)
    if review.date_end is not None:
        return Result({"project": project, "review": review})

    form = forms.EndReview(data)
    result = Result({"project": project, "review": review, "form": form})
    if method == "POST" and form.validate():
        review.date_end = datetime.utcnow()
        # TODO: store review result in model
        # review.approved = form.approved.data
        if form.approved.data:
            project.state = "done"
            success_message = "Project review approved"
        else:
            project.state = "rejected"
            success_message = "Project review declined"
        try:
            db.commit()
        except SQLAlchemyError:
            result.flash.append(("An error occurred while adding your "
                "review, please contact an administrator.", "danger"))
        else:
            result.flash.append((success_message, "success"))
    return result

def newreview(db, method, data, pname, username):
    project, err_result = _lookup_project(db, pname)
    if project is None:
        return err_result
    form = forms.NewReview(data)
    result = Result({"project": project, "form": form})
    if method == "POST" and form.validate():
        last_review = project.last_review
        if last_review is not None and last_review.date_end is None:
            result.flash.append(("Review already in progress.", "danger"))
            return result
        review = Review(
            project_id=project.id,
            reason=form.reason.data
        )
        db.add(review)
        project.state = "review"
        try:
            db.commit()
        except SQLAlchemyError:
            result.flash.append(("An error occurred while adding your "
                "project, please contact an administrator.", "danger"))
        else:
            result.flash.append(("Review successfully started!", "success"))
            result.redirect = ('review', {"pname": project.name,
                                          "rid": review.id})
    return result

# User specific pages

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
