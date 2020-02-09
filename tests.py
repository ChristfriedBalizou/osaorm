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

from models import Parent, Child


def test_type_error_bulk_save_objects():
    with pytest.raises(TypeError):
        assert Child.objects.bulk_save_objects([Parent(), Child()])


def test_parent_bulk_save_objects():
    Parent.objects.bulk_save_objects([Parent(), Parent()])
    assert Parent.objects.count() == 2


def test_child_bulk_save_objects():
    parent1 = Parent()
    parent2 = Parent()

    # Create parents
    Parent.objects.bulk_save_objects([parent1, parent2], return_defaults=True)
    assert Parent.objects.count() == 2

    # Create children
    children1 = [Child(parent_id=parent1.id) for _ in range(5)]
    children2 = [Child(parent_id=parent2.id) for _ in range(16)]

    Child.objects.bulk_save_objects(children1 + children2, return_defaults=True)
    assert Child.objects.filter(Child.parent_id==parent1.id).count() == 5
    assert Child.objects.filter(Child.parent_id==parent2.id).count() == 16
