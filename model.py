import sqlalchemy.ext.declarative as declarative

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey

import manager

BASE = declarative.declarative_base(cls=manager.Manager)


class Parent(BASE):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    children = relationship("Child")


class Child(BASE):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'))


BASE.metadata.drop_all(manager.ENGINE)
BASE.metadata.create_all(manager.ENGINE)
""" Drop the existing database and create a new one
"""
