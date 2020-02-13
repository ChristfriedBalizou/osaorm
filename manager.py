#         _\|/_
#         (o o)
# +----oOO-{_}-OOo---------------------------------------------------------+
# |  This class is where will do the whole magic.                          |
# |  We will create and abstract manager class to controll the session.    |
# |                                                                        |
# +------------------------------------------------------------------------+

import os
import contextlib

import sqlalchemy
from sqlalchemy import ForeignKey, Column, Integer
from sqlalchemy.orm import query, sessionmaker
from sqlalchemy.ext.declarative import declared_attr


CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
SQLITE_DB = f"sqlite:///{CURRENT_DIRECTORY}/osaorm.db"
"""Setup SQLite database storage
"""

ENGINE = sqlalchemy.create_engine(SQLITE_DB, echo=True)
Session = sessionmaker(bind=ENGINE)


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


@contextlib.contextmanager
def transaction_scope():
    """Inspired from SQLalchemy managing transaction
    https://docs.sqlalchemy.org/en/13/orm/session_transaction.html#managing-transactions
    """
    sess = Session()

    try:
        yield sess
    except:
        raise
    else:
        sess.commit()
    finally:
        sess.close()


class QueryManager(query.Query):

    def __init__(self, klass):

        self.klass = klass

        with transaction_scope() as transaction:
            """Create a transaction scope which close after
            after usage.
            """
            super(QueryManager, self).__init__(klass, session=transaction)

    def bulk_save_objects(self, entities, **kwargs):
        if False in {isinstance(e, self.klass) for e in entities}:
            raise TypeError(
                f"All models should be of type {self.klass.__name__}"
            )

        with transaction_scope() as transaction:
            return transaction.bulk_save_objects(entities, **kwargs)

    def save(self, entity, **kwargs):
        """This function use session.Session.bulk_save_objects
        to update or create new instance
        """
        self.bulk_save_objects(
            [entity],
            return_defaults=True,
            **kwargs
        )

    def is_modified(self, entity, **kwargs):
        """Read sqlalchemy.orm.session.Session.is_modified
        from sqlalchemy documentation to understand how the
        is_modified works. This function is a wrapper
        """

        if not isinstance(entity, self.klass):
            raise TypeError(
                f"Entity should be of type {self.klass.__name__}"
            )

        with transaction_scope() as transaction:
            return transaction.is_modified(entity, **kwargs)


class Manager(object):
    """The Manager inherit from sqlalchemy.orm.session.Session
    class and override public function to behave directly as
    python class method.
    """

    @declared_attr
    def __tablename__(cls):
        return csl.__name__.lower()

    @property
    def klass(self):
        return self.__class__

    @classproperty
    def objects(cls):
        """All available methods under sqlalchemy.orm.query.Query
        are now available on objects attribute.
        """
        return QueryManager(cls)

    def save(self, **kwargs):
        return QueryManager(self.klass).save(self, **kwargs)

    def is_modified(self, **kwargs):
        return QueryManager(self.klass).is_modified(self, **kwargs)

    id = Column(Integer, primary_key=True)
