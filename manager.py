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


def transaction(instance, wrapped):
    """Transaction decorator will surround
    an sqlalchemy base function and handle
    the transaction scope. Rollback in case an
    exception happened otherwise commit the session
    """

    def wrapper(*args, **kwargs):
        try:
            result = wrapped(*args, **kwargs)
        except Exception as exception:
            instance.session.rollback()
            raise exception from None
        else:
            return result
        finally:
            instance.session.commit()

    return wrapper


def transactional(Class):
    """This function will create a transactional
    session. This will keep the session transaction
    and allow rollback if required otherwise commit the
    session and restart a new one.

    #sqlalchemy.orm.session.Session.params.autocommit
    """

    class WrapperClass:

        def __init__(self, *args, **kwargs):
            self.wrapped = Class(*args, **kwargs)

        def __getattribute__(self, name):
            """This method will be called whenever any attribute of class
            WrapperClass is accessed.

            If the accessed method is part of the wrapped class
            a transaction is opened around the method to rollback
            in case of exception or commit if everything goes well.
            """

            try:
                attribute = super(WrapperClass, self).__getattribute__(name)
            except AttributeError:
                pass
            else:
                return attribute

            attribute = self.wrapped.__getattribute__(name)

            if type(attribute) == type(self.__init__):
                # Check if the attribute gotten is a method or an
                # attribute. The transaction will only be apply to
                # method's.
                return transaction(self, attribute)

            return attribute

    return WrapperClass


@transactional
class QueryManager(query.Query):

    def __init__(self, klass):

        self.klass = klass
        self.session = session.Session(bind=ENGINE)

        super().__init__(klass, session=self.session)

    def bulk_save_objects(self, entities, **kwargs):
        if False in {isinstance(e, self.klass) for e in entities}:
            raise TypeError(
                f"All models should be of type {self.klass.__name__}"
            )

        self.session.bulk_save_objects(entities, **kwargs)

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

        return self.session.is_modified(entity, **kwargs)


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
