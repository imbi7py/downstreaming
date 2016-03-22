# -*- coding: utf-8 -*-
# pylint: disable=bad-whitespace,no-init,too-few-public-methods,bad-continuation,invalid-name

from __future__ import absolute_import, unicode_literals, print_function

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

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
    # TODO: derive the project state from the underlying review status
    # "new" -> last_review is None
    # "review" -> last_review.date_end is None
    # "rejected" -> last_review.approved is False
    # "approved" -> last_review.approved is True
    state       = sa.Column(sa.String(64),
                            nullable=False, default="new", index=True)
    submitted   = sa.Column(sa.DateTime,
                            index=True, nullable=False, default=sa.func.now())
    reviews     = sa.orm.relationship("Review", back_populates="project",
                                      order_by="Review.id")

    def __repr__(self):
        return '<Project %r>' % (self.name)

    @property
    def last_review(self):
        return sa.orm.object_session(self).query(Review).with_parent(self
            ).order_by(Review.id.desc()).first()

class Review(Base):
    __tablename__ = 'reviews'

    id         = sa.Column(sa.Integer, primary_key=True)
    project_id = sa.Column(sa.Integer,
                           sa.ForeignKey("projects.id",
                           ondelete="cascade", onupdate="cascade"))
    project    = sa.orm.relationship("Project", back_populates="reviews")
    reason = sa.Column(sa.Text, nullable=False)
    approved = sa.Column(sa.Boolean)
    date_start = sa.Column(sa.DateTime,
                           index=True, nullable=False, default=sa.func.now())
    date_end   = sa.Column(sa.DateTime, index=True)

    def __repr__(self):
        return '<Review %r of project %r>' % (self.id, self.project_id)
