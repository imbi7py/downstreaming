# -*- coding: utf-8 -*-
# pylint: disable=bad-whitespace,no-init,too-few-public-methods,bad-continuation,invalid-name

from __future__ import absolute_import, unicode_literals, print_function

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy


Base = declarative_base()

# TODO: add relationships


class Project(Base):
    """
    A project proposed for review and inclusion.
    """
    __tablename__ = 'projects'

    id          = sa.Column(sa.Integer, primary_key=True)
    name        = sa.Column(sa.String(128),
                            nullable=False, index=True, unique=True)
    summary     = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=False)
    owner       = sa.Column(sa.String(255))
    # The state could use an Enum type, but we don't need the space-savings and
    # strict model checks that come with the added complexity in migrations.
    # TODO: when we setup a workflow engine, extract the entry state here
    # TODO: derive the project state from the underlying review status
    state       = sa.Column(sa.String(64),
                            nullable=False, default="new", index=True)
    submitted   = sa.Column(sa.DateTime,
                            index=True, nullable=False, default=sa.func.now())
    requires    = sa.Column(sa.Integer,
                            sa.ForeignKey("projects.id", onupdate="cascade"))
    reviews     = sa.orm.relationship("Review", back_populates="project",
                                      order_by="Review.id")

    def __repr__(self):
        return '<Project %r>' % (self.name)

    @property
    def last_review(self):
        return sa.orm.object_session(self).query(Review).with_parent(self
            ).order_by(Review.id.desc()).first()

    @property
    def last_review_activity(self):
        # TODO: cache this
        req = sa.orm.object_session(self
            ).query(Comment.date).join(Review
            ).filter(Review.project_id == self.id
            ).order_by(Comment.date.desc()).first()
        if req is None:
            return None
        return req.date

    @hybrid_property
    def active(self):
        # I'm pretty sure we'll end up needing a workflow engine, if we
        # want to make the app easily configurable. Then we can extract the
        # exit states here instead of hardcoding.
        # TODO: use a workflow engine.
        return self.state not in ["done", "rejected"]
    @active.expression
    def active(cls):
        return sa.not_(cls.state.in_(["done", "rejected"]))


class Review(Base):
    __tablename__ = 'reviews'

    id         = sa.Column(sa.Integer, primary_key=True)
    project_id = sa.Column(sa.Integer,
                           sa.ForeignKey("projects.id",
                           ondelete="cascade", onupdate="cascade"))
    project    = sa.orm.relationship("Project", back_populates="reviews")
    reason = sa.Column(sa.Text, nullable=False)
    date_start = sa.Column(sa.DateTime,
                           index=True, nullable=False, default=sa.func.now())
    date_end   = sa.Column(sa.DateTime, index=True)
    reviewers_obj = sa.orm.relationship("Reviewer")
    reviewers  = association_proxy('reviewers_obj', 'reviewer_name')

    def __repr__(self):
        return '<Review %r of project %r>' % (self.id, self.project_id)


class Reviewer(Base):
    __tablename__ = 'reviewers'

    review_id     = sa.Column(sa.Integer,
                              sa.ForeignKey('reviews.id'), primary_key=True)
    reviewer_name = sa.Column(sa.String(255), primary_key=True)


class Watcher(Base):
    __tablename__ = 'watchers'

    project_id   = sa.Column(sa.Integer,
                             sa.ForeignKey('projects.id'), primary_key=True)
    watcher_name = sa.Column(sa.String(255), primary_key=True)


class Comment(Base):
    __tablename__ = 'comments'

    id          = sa.Column(sa.Integer, primary_key=True)
    review_id   = sa.Column(sa.Integer,
                            sa.ForeignKey("reviews.id",
                                ondelete="cascade", onupdate="cascade"))
    author      = sa.Column(sa.String(255), index=True)
    date        = sa.Column(sa.DateTime, index=True, nullable=False, default=sa.func.now())
    line_number = sa.Column(sa.Integer)
    # relevant: has the comment been replied to?
    relevant    = sa.Column(sa.Boolean, index=True, nullable=False, default=True)

    def __repr__(self):
        return '<Comment %r on %r>' % (self.id, self.review_id)
