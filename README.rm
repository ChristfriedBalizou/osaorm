# OSaORM

Stand for Overrided Sqlalchemy ORM.

Django framework ORM has been from far the best ORM I used so fare in python.
Recently switched to python after some longtime working with Django ORM make me
realize how easy it was.

The simplicity is the access to the database connection. Django ORM provide a
Manager which is embed into your model and allow you to do:
```python
Model.objects.fileter
Model.objects.create
Model.objects.count
Model.objects.bulk_create
...
```

With Sqlalchemy if you are a fan of scopes (as me) you do:
```python

with session_scope() as sess:

    # With Query API
    sess.query(Model).filter
    sess.query(Model).count()
    ...

    # With Session API
    sess.bulk_create
    ...
```

The point here is that you have to create a session and use the query API or the
session API to achieve your request. In Django the `objects` on your model
manage the session (implicitly) for you.


The goal of this repo is to be able to achieve the same goal using SQLalchemy.

Note that this project will not cover all the cases we will on handle the
session management part at keep using Sqlalchemy Session and Query API
accessible either via `query` or `objects` keyword.
