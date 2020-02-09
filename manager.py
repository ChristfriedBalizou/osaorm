#         _\|/_
#         (o o)
# +----oOO-{_}-OOo---------------------------------------------------------+
# |  This class is where will do the whole magic.                          |
# |  We will create and abstract manager class to controll the session.    |
# |                                                                        |
# +------------------------------------------------------------------------+

import os

import sqlalchemy
from sqlalchemy.orm import session, query
from sqlalchemy import ForeignKey, Column, Integer
from sqlalchemy.ext.declarative import declared_attr


CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
SQLITE_DB = f"sqlite:///{CURRENT_DIRECTORY}/osaorm.db"
"""Setup SQLite database storage
"""

ENGINE = sqlalchemy.create_engine(SQLITE_DB, echo=True)


class classproperty(object):
    """Create a class property decorator
    to access the objects attribute.

    This decorator allow us to access the class
    from a property decorated method.
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls):
        return self.func(cls)


def commit(func):
    """This function will automatically call commit
    after each function call
    """
    def decorator(self, *args, **kwargs):

        try:
            return func(self, *args, **kwargs)
        except Exception as exception:
            self.session.rollback()
            raise exception from None
        finally:
            self.session.commit()

    return decorator


class QueryManager(query.Query):

    def __init__(self, klass):

        self.klass = klass
        self.session = session.Session(bind=ENGINE)
        super(QueryManager, self).__init__(self.klass, session=self.session)

    @commit
    def bulk_save_objects(self, entities, **kwargs):
        if False in {isinstance(e, self.klass) for e in entities}:
            raise TypeError(
                f"All models should be of type {self.klass.__name__}"
            )

        self.session.bulk_save_objects(entities, **kwargs)


class Manager(object):
    """The Manager inherit from sqlalchemy.orm.session.Session
    class and override public function to behave directly as
    python class method.
    """

    @declared_attr
    def __tablename__(cls):
        return csl.__name__.lower()

    @classproperty
    def objects(cls):
        """All available methods under sqlalchemy.orm.query.Query
        are now available on objects attribute.
        """
        return QueryManager(cls)

    id = Column(Integer, primary_key=True)
