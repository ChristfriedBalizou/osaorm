import os
import contextlib
import traceback

import sqlalchemy
import sqlalchemy.ext.declarative as declarative

from sqlalchemy.orm import session, relationship
from sqlalchemy import Column, Integer, ForeignKey


CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
SQLITE_DB = f"sqlite:///{CURRENT_DIRECTORY}/osaorm.db"
"""Setup SQLite database storage
"""

ENGINE = sqlalchemy.create_engine(SQLITE_DB, echo=True)
BASE = declarative.declarative_base()


@contextlib.contextmanager
def session_scope():
    """This function create a transactional
    session to make sure everything is going
    well before closing
    """

    sess = session.Session(bind=ENGINE)

    try:
        yield sess
        sess.commit()
    except Exception:
        sess.rollback()
        traceback.print_exc()
    finally:
        sess.close()


class Parent(BASE):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    children = relationship("Child")


class Child(BASE):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'))


BASE.metadata.drop_all(ENGINE)
BASE.metadata.create_all(ENGINE)
""" Drop the existing database and create a new one
"""


"""
         _\|/_
         (o o)
 +----oOO-{_}-OOo---------------------------------------------------------+
 |                                                                        |
 |  Creating a test suit to create a two parents and bunch of child each  |
 |                                                                        |
 +------------------------------------------------------------------------+
"""

with session_scope() as sess:
    parent1 = Parent()
    parent2 = Parent()

    # Create parents
    sess.bulk_save_objects([parent1, parent2], return_defaults=True)
    assert sess.query(Parent).count() == 2

    # Create children
    children1 = [Child(parent_id=parent1.id) for _ in range(5)]
    children2 = [Child(parent_id=parent2.id) for _ in range(16)]

    sess.bulk_save_objects(children1 + children2, return_defaults=True)
    assert sess.query(Child).filter(Child.parent_id==parent1.id).count() == 5
    assert sess.query(Child).filter(Child.parent_id==parent2.id).count() == 16
