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

from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from .. import forms
from .models import Project, Review
from .utils import Result


def index(db):
    recent_projects = db.query(Project
        ).order_by(Project.submitted.desc()).limit(10).all()
    active_reviews = db.query(Project).join(Review
        ).filter(Review.date_end.is_(None)
        ).order_by(Review.date_start.desc()).limit(10).all()
    unreviewed_projects = db.query(Project).filter(~Project.reviews.any()
        ).order_by(Project.submitted.desc()).limit(10).all()
    return Result({"recent_projects": recent_projects,
                   "updated_revs": active_reviews,
                   "projects_without_rev": unreviewed_projects
                   })


def _lookup_item(db_query, error_message):
    try:
        item = db_query.one()
    except NoResultFound:
        return None, Result({"message": error_message()}, code=404)
    else:
        return item, None

def _lookup_project(db, name):
    return _lookup_item(db.query(Project).filter_by(name=name),
                        lambda: "Unknown project: {}".format(name))

# Project display and registration

def projects(db):
    # TODO: Order by start date of most recent review (unreviewed first)
    items = db.query(Project).order_by(Project.submitted.desc()).all()
    return Result({"projects": items})

def project(db, name):
    item, err_result = _lookup_project(db, name)
    if item is not None:
        return Result({"project": item})
    return err_result

def newproject(db, method, data, username):
    form = forms.NewProject(data)
    result = Result({"form": form})
    if method == "POST" and form.validate():
        new_project = Project(
            name=form.name.data,
            summary=form.summary.data,
            description=form.description.data,
            owner=username,
            )
        db.add(new_project)
        try:
            db.commit()
        except SQLAlchemyError:
            result.flash.append(("An error occurred while adding your "
                "project, please contact an administrator.", "danger"))
        else:
            result.flash.append(("Project successfully created!", "success"))
            result.redirect = ('project', {"name": new_project.name})

    return result

# Review display and registration

def reviews(db, pname):
    parent_project, err_result = _lookup_project(db, pname)
    if parent_project is None:
        return err_result
    items = db.query(Review).join(Project).order_by(Review.id.desc()).all()
    return Result({"project": parent_project, "reviews": items})

def review(db, method, data, pname, rid):
    parent_project, err_result = _lookup_project(db, pname)
    if parent_project is None:
        return err_result
    try:
        this_review = db.query(Review).join(Project).filter(Review.id==rid).one()
    except NoResultFound:
        err_message = "Unknown review ID for {}: {}".format(pname, rid)
        return Result({"message": err_message}, code=404)
    if this_review.date_end is not None:
        return Result({"project": parent_project, "review": this_review})

    form = forms.EndReview(data)
    result = Result({"project": parent_project, "review": this_review, "form": form})
    if method == "POST" and form.validate():
        this_review.date_end = datetime.utcnow()
        this_review.approved = form.approved.data
        if form.approved.data:
            parent_project.state = "approved"
            success_message = "Project status is now approved"
        else:
            parent_project.state = "rejected"
            success_message = "Project status is now rejected"
        try:
            db.commit()
        except SQLAlchemyError:
            result.flash.append(("An error occurred while adding your "
                "review, please contact an administrator.", "danger"))
        else:
            result.flash.append((success_message, "success"))
    return result

def newreview(db, method, data, pname, username):
    parent_project, err_result = _lookup_project(db, pname)
    if parent_project is None:
        return err_result
    form = forms.NewReview(data)
    result = Result({"project": parent_project, "form": form})
    if method == "POST" and form.validate():
        last_review = parent_project.last_review
        if last_review is not None and last_review.date_end is None:
            result.flash.append(("Review already in progress.", "danger"))
            return result
        new_review = Review(
            project_id=parent_project.id,
            reason=form.reason.data
        )
        db.add(new_review)
        parent_project.state = "review"
        try:
            db.commit()
        except SQLAlchemyError:
            result.flash.append(("An error occurred while adding your "
                "project, please contact an administrator.", "danger"))
        else:
            result.flash.append(("Review successfully started!", "success"))
            result.redirect = ('review', {"pname": parent_project.name,
                                          "rid": new_review.id})
    return result

# User specific pages

def user_projects(db, username):
    # TODO: Track project responsibility/point-of-contact info
    active_projects = db.query(Project).filter(
                        Project.state.in_(["new", "review"])).all()
    approved_projects = db.query(Project).filter(
                          Project.state == "approved").all()
    rejected_projects = db.query(Project).filter(
                          Project.state == "rejected").all()
    return Result({"projects": active_projects,
                   "approved_projects": approved_projects,
                   "rejected_projects": rejected_projects,
                   })


def user_reviews(db, username):
    # TODO: Track review responsibility/point-of-contact info
    linked_reviews = db.query(Review).order_by(Review.date_start.desc()).all()
    return Result({"reviews": linked_reviews})
