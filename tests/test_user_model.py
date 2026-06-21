"""Tests for the User model — src/models.py."""

import pytest

from src.orm import BaseModel, Database, ModelMeta


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_everything():
    """Reset DB and registry, then import User fresh so the table is recreated."""
    Database.reset()
    ModelMeta.reset_registry()

    # Purge models module so User gets recreated with fresh registry
    import sys
    sys.modules.pop("src.models", None)

    from src.models import User
    yield User

    Database.reset()
    ModelMeta.reset_registry()
    sys.modules.pop("src.models", None)


# ── User tests ────────────────────────────────────────────────────────────────

def test_create_user(reset_everything):
    """Creating and saving a User works."""
    User = reset_everything
    u = User(name="Alice", email="alice@example.com", age=30)
    assert u.id is None
    u.save()
    assert u.id == 1


def test_find_user(reset_everything):
    """A saved User can be retrieved by id."""
    User = reset_everything
    u = User(name="Bob", email="bob@example.com", age=25)
    u.save()

    found = User.find(u.id)
    assert found is not None
    assert found.name == "Bob"
    assert found.email == "bob@example.com"
    assert found.age == 25


def test_find_nonexistent_user(reset_everything):
    """Finding a non-existent user returns None."""
    User = reset_everything
    assert User.find(42) is None


def test_update_user(reset_everything):
    """Modifying a field and calling save() persists the change."""
    User = reset_everything
    u = User(name="Charlie", email="charlie@old.com", age=28)
    u.save()

    u.email = "charlie@new.com"
    u.age = 29
    u.save()

    found = User.find(u.id)
    assert found.email == "charlie@new.com"
    assert found.age == 29
    assert found.name == "Charlie"  # unchanged


def test_delete_user(reset_everything):
    """Deleting a user removes it from the database."""
    User = reset_everything
    u = User(name="Dave", email="dave@example.com", age=40)
    u.save()
    uid = u.id

    u.delete()
    assert User.find(uid) is None


def test_delete_unsaved_user(reset_everything):
    """Deleting a user that was never saved raises ValueError."""
    User = reset_everything
    u = User(name="Eve", email="eve@example.com", age=22)
    with pytest.raises(ValueError, match="Cannot delete an instance with no id"):
        u.delete()


def test_user_repr(reset_everything):
    """repr of a User shows the class name and id."""
    User = reset_everything
    u = User(name="Frank", email="frank@example.com", age=35)
    assert repr(u) == "User(id=None)"
    u.save()
    assert repr(u) == "User(id=1)"


def test_multiple_users(reset_everything):
    """Creating several users and calling all() returns all of them."""
    User = reset_everything
    User(name="A", email="a@x.com", age=10).save()
    User(name="B", email="b@x.com", age=20).save()
    User(name="C", email="c@x.com", age=30).save()

    users = User.all()
    assert len(users) == 3
    names = [u.name for u in users]
    assert names == ["A", "B", "C"]


def test_user_missing_fields(reset_everything):
    """Creating a User with partial fields sets omitted ones to None."""
    User = reset_everything
    u = User(name="Partial")
    u.save()

    found = User.find(u.id)
    assert found.name == "Partial"
    assert found.email is None
    assert found.age is None


def test_user_email_unique(reset_everything):
    """Two users can have different emails (no UNIQUE constraint by default)."""
    User = reset_everything
    u1 = User(name="G", email="g@x.com", age=15)
    u2 = User(name="H", email="h@x.com", age=20)
    u1.save()
    u2.save()

    assert User.find(u1.id).email == "g@x.com"
    assert User.find(u2.id).email == "h@x.com"
    assert len(User.all()) == 2
