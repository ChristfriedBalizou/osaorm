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
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey, Column, Integer
from sqlalchemy.ext.declarative import declared_attr


CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
SQLITE_DATABASE = f"sqlite:///{CURRENT_DIRECTORY}/osaorm.db"
"""Setup SQLite database storage
"""

ENGINE = sqlalchemy.create_engine(SQLITE_DATABASE, echo=True)
Session = sessionmaker(bind=ENGINE, autocommit=True)
ScopedSession = scoped_session(Session)


@contextlib.contextmanager
def transactional_scope():
    """Inspired from SQLalchemy managing transaction
    https://docs.sqlalchemy.org/en/13/orm/session_transaction.html#managing-transactions
    """
    sess = Session()

    try:
        sess.begin()
        yield sess
    except Exception:
        raise
    else:
        sess.commit()
    finally:
        sess.close()


class Manager(object):
    """The Manager inherit from sqlalchemy.orm.session.Session
    class and override public function to behave directly as
    python class method.
    """

    objects = ScopedSession.query_property()
    """All available methods under sqlalchemy.orm.query.Query
    are now available on objects attribute.
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def bulk_save_objects(cls, entities, **kwargs):
        """This function use session.Session.bulk_save_objects
        to update or create new instance
        """
        if False in {isinstance(e, cls) for e in entities}:
            raise TypeError(
                f"All models should be of type {cls.__name__}"
            )

        with transactional_scope() as transaction:
            transaction.bulk_save_objects(
                entities,
                return_defaults=True,
                update_changed_only=True
            )

    def save(self, **kwargs):
        """This function use session.Session.bulk_save_objects
        to update or create new instance
        """
        self.__class__.bulk_save_objects([self], **kwargs)

    def is_modified(self, **kwargs):
        """Read sqlalchemy.orm.session.Session.is_modified
        from sqlalchemy documentation to understand how the
        is_modified works. This function is a wrapper
        """
        with transactional_scope() as transaction:
            return transaction.is_modified(self, **kwargs)

    id = Column(Integer, primary_key=True)
