# -*- coding: utf-8 -*-

'''
Views for the main web service
'''

from __future__ import absolute_import, unicode_literals, print_function

import os
import flask
from flask.ext.fas import fas_login_required
from six import string_types

from . import APP, FAS
from .utils import is_safe_url, is_authenticated, handle_result
from .lib import views


@APP.route("/")
def index():
    result = views.index(flask.g.db)
    return handle_result(result, 'index.html')

@APP.route("/search")
def search():
    raise NotImplementedError

@APP.route("/projects")
def projects():
    result = views.projects(flask.g.db)
    return handle_result(result, 'projects.html')

@APP.route("/projects/<name>")
def project(name):
    result = views.project(flask.g.db, name)
    return handle_result(result, 'project.html')

@APP.route("/projects/<pname>/reviews/")
def reviews(pname):
    return flask.render_template("simple.html", content="reviews for project %s" % pname)

@APP.route("/projects/<pname>/reviews/<int:rid>")
def review(pname, rid):
    return flask.render_template("simple.html", content="review %d" % rid)

@APP.route("/projects/<pname>/reviews/new")
def newreview(pname):
    return flask.render_template("simple.html", content="new review for project %s" % pname)


@APP.route("/new", methods=["GET", "POST"])
@fas_login_required
def newproject():
    result = views.newproject(
        flask.g.db, flask.request.method, flask.request.form,
        flask.g.fas_user.username)
    return handle_result(result, 'new.html')


@APP.route("/my/projects")
@fas_login_required
def user_projects():
    result = views.user_projects(flask.g.db, flask.g.fas_user.username)
    return flask.render_template("user/projects.html", **result.context)

@APP.route("/my/reviews")
@fas_login_required
def user_reviews():
    result = views.user_reviews(flask.g.db, flask.g.fas_user.username)
    return flask.render_template("user/reviews.html", **result.context)


# Login / logout

@APP.route('/login', methods=['GET', 'POST'])
def auth_login():
    next_url = flask.url_for('index')
    if 'next' in flask.request.values:
        url = flask.request.values['next']
        if is_safe_url(url) and url != flask.url_for('auth_login'):
            next_url = url

    if is_authenticated():
        return flask.redirect(next_url)

    required_groups = set(APP.config['REQUIRED_GROUPS'])
    if isinstance(APP.config['ADMIN_GROUPS'], string_types):
        required_groups.add(APP.config['ADMIN_GROUPS'])
    else:
        required_groups.update(APP.config['ADMIN_GROUPS'])
    return FAS.login(return_url=next_url, groups=required_groups)


@APP.route('/logout')
def logout():
    if flask.g.fas_user:
        flask.flash("Sucessfully disconnected, goodbye!", "success")
        FAS.logout()
    return flask.redirect(flask.url_for('index'))
