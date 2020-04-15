# oSAORM

Stand for `Overrided SQLAchemy ORM`.

Django framework ORM have been from far the best ORM I used so fare in python.
Recently switched to SQLAlchemy after some longtime working with Django ORM make me
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

## Documentation

The `Manager` class offer to every models that inherit it the following
methods:

- objects
- save
- is_modified


### Objects

The `objects` attribute is a class property which offer you all access to the [sqlalchemy.query.Query](https://docs.sqlalchemy.org/en/13/orm/query.html#query-api)

```python
# Let's count all User(s) from the User table
User.objects.count()

# Let's filter age equal to 56
User.objects.filter(User.age == 56)
# or
User.objects.filter_by(age=56)

# Save a list of User(s)
User.bulk_save_objects([User() for _ in range(5)])
```

### Save

The `save` function is directly linked to the instance of the class 
and actually save and update. It is an abstraction of `bulk_save_objects`.

```python
user = User()
user.save() # Creation

user.name = "foobar"
user.save() # Update
```

### Is modified
The `ìs_modified` function is nice to have function to check if the instance
you are working on is desynchronize from the database.

```python

user = User()
user.save() # Creation

user.name = "foobar"
user.is_modified() # True
```
