"""
         _\|/_
         (o o)
 +----oOO-{_}-OOo---------------------------------------------------------+
 |                                                                        |
 |  Creating a test suit to create a two parents and bunch of child each  |
 |                                                                        |
 +------------------------------------------------------------------------+
"""
import pytest

from model import Parent, Child


def test_type_error_bulk_save_objects():
    with pytest.raises(TypeError):
        Child.objects.bulk_save_objects([Parent(), Child()])


def test_parent_bulk_save_objects():
    Parent.objects.bulk_save_objects([Parent(), Parent()])
    assert Parent.objects.count() == 2


def test_child_bulk_save_objects():
    parent1, parent2 = Parent.objects.all()

    children1 = [Child(parent_id=parent1.id) for _ in range(5)]
    children2 = [Child(parent_id=parent2.id) for _ in range(16)]

    Child.objects.bulk_save_objects(children1 + children2, return_defaults=True)
    assert Child.objects.filter(Child.parent_id==parent1.id).count() == 5
    assert Child.objects.filter(Child.parent_id==parent2.id).count() == 16


def test_save_and_update():
    parent = Parent()
    parent.save()

    assert parent.id != None
    assert Parent.objects.count() == 3

    # Update
    child = Child()
    child.save()

    assert child.parent_id == None
    child.parent_id = parent.id
    child.save()

    assert Child.objects.count() == 22
    assert child.parent_id == parent.id


def test_delete():
    assert Parent.objects.filter_by(id=1).count() == 1
    Parent.objects.filter_by(id=1).delete()

    assert Parent.objects.filter_by(id=0).count() == 0


def test_is_modified():
    child = Child.objects.first()
    assert child.is_modified() == False

    child.parent_id = 0
    assert child.is_modified() == True
