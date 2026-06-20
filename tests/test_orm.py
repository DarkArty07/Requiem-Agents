"""Tests for the mini ORM — src/orm.py."""

import pytest

from src.orm import BaseModel, Database, ModelMeta, _create_table, _get_fields


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_everything():
    """Reset database and model registry before each test for full isolation."""
    Database.reset()
    ModelMeta.reset_registry()
    yield
    Database.reset()
    ModelMeta.reset_registry()


# ── Helper: dynamically create a test model ───────────────────────────────────

def _make_model(tablename: str, **fields: type):
    """Create a throwaway model class for testing.

    Args:
        tablename: The SQL table name.
        **fields: Field names mapped to Python types.

    Returns:
        A new BaseModel subclass.
    """
    namespace = {"__tablename__": tablename, "__annotations__": dict(fields)}
    return ModelMeta(f"Test_{tablename}", (BaseModel,), namespace)


# ── Database ──────────────────────────────────────────────────────────────────

def test_database_connect():
    """Connecting in memory returns a valid sqlite3 connection."""
    conn = Database.connect(":memory:")
    assert conn is not None
    tables = Database.fetchall(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    assert isinstance(tables, list)


def test_database_execute():
    """Execute creates a table and inserts data."""
    Database.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, x TEXT)")
    Database.execute("INSERT INTO test (x) VALUES (?)", ("hello",))
    row = Database.fetchone("SELECT x FROM test WHERE id = 1")
    assert row["x"] == "hello"


# ── Model registry ────────────────────────────────────────────────────────────

def test_model_registry():
    """ModelMeta._models contains registered models."""
    M = _make_model("items", name=str, price=float)
    assert "items" in ModelMeta._models
    assert ModelMeta._models["items"] is M


def test_model_registry_multiple():
    """Multiple models all appear in the registry."""
    A = _make_model("alpha", a=int)
    B = _make_model("beta", b=str)
    assert "alpha" in ModelMeta._models
    assert "beta" in ModelMeta._models
    assert ModelMeta._models["alpha"] is A
    assert ModelMeta._models["beta"] is B


# ── Table creation ────────────────────────────────────────────────────────────

def test_table_creation():
    """Table is auto-created when a model class is defined."""
    M = _make_model("gadgets", name=str, stock=int)
    rows = Database.fetchall(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='gadgets'"
    )
    assert len(rows) == 1


def test_field_extraction():
    """_get_fields returns declared fields, excluding id and private attrs."""
    M = _make_model("example", title=str, count=int, _private=str)
    fields = _get_fields(M)
    assert fields == {"title": str, "count": int}


# ── save ──────────────────────────────────────────────────────────────────────

def test_save_insert():
    """save() on a new instance does INSERT and assigns an id."""
    M = _make_model("notes", content=str)
    note = M(content="hello")
    assert note.id is None
    note.save()
    assert note.id == 1


def test_save_update():
    """save() on an existing instance does UPDATE, id stays the same."""
    M = _make_model("posts", title=str)
    post = M(title="original")
    post.save()
    original_id = post.id

    post.title = "updated"
    post.save()
    assert post.id == original_id

    # Verify the update persisted
    found = M.find(original_id)
    assert found.title == "updated"


def test_save_twice():
    """Saving twice does not duplicate the record."""
    M = _make_model("entries", value=int)
    entry = M(value=42)
    entry.save()
    entry.save()  # second save should UPDATE, not INSERT
    assert len(M.all()) == 1


# ── find ──────────────────────────────────────────────────────────────────────

def test_find_existing():
    """find(id) returns the correct instance."""
    M = _make_model("books", title=str)
    book = M(title="Dune")
    book.save()

    found = M.find(book.id)
    assert found is not None
    assert found.id == book.id
    assert found.title == "Dune"


def test_find_nonexistent():
    """find() with a non-existing id returns None."""
    M = _make_model("ghosts", name=str)
    assert M.find(999) is None


# ── delete ────────────────────────────────────────────────────────────────────

def test_delete_existing():
    """delete() removes the record; find() returns None afterwards."""
    M = _make_model("files", path=str)
    f = M(path="/tmp/x")
    f.save()
    fid = f.id

    f.delete()
    assert M.find(fid) is None


def test_delete_without_id():
    """delete() on an unsaved instance raises ValueError."""
    M = _make_model("items", label=str)
    item = M(label="orphan")
    with pytest.raises(ValueError, match="Cannot delete an instance with no id"):
        item.delete()


# ── all ───────────────────────────────────────────────────────────────────────

def test_all_empty():
    """all() on an empty table returns []."""
    M = _make_model("void", attr=str)
    assert M.all() == []


def test_all_multiple():
    """all() returns all instances in insertion order."""
    M = _make_model("nums", value=int)
    for i in range(5):
        M(value=i).save()
    results = M.all()
    assert len(results) == 5
    assert [r.value for r in results] == [0, 1, 2, 3, 4]


# ── repr ──────────────────────────────────────────────────────────────────────

def test_repr():
    """repr shows class name and id."""
    M = _make_model("widgets", name=str)
    w = M(name="gizmo")
    assert repr(w) == "Test_widgets(id=None)"
    w.save()
    assert repr(w) == "Test_widgets(id=1)"


# ── Field types ───────────────────────────────────────────────────────────────

def test_field_types():
    """int, str, float, and bool are stored and retrieved correctly."""
    M = _make_model("typed", count=int, label=str, price=float, active=bool)
    obj = M(count=10, label="test", price=9.99, active=True)
    obj.save()

    found = M.find(obj.id)
    assert found.count == 10
    assert found.label == "test"
    assert found.price == 9.99
    assert found.active == 1  # SQLite stores bool as INTEGER


def test_field_defaults_none():
    """Omitted fields default to None."""
    M = _make_model("partial", a=str, b=int, c=float)
    obj = M(a="only")
    obj.save()
    found = M.find(obj.id)
    assert found.a == "only"
    assert found.b is None
    assert found.c is None


# ── Multiple models ───────────────────────────────────────────────────────────

def test_multiple_models_independent():
    """Two different models do not interfere with each other."""
    M1 = _make_model("cats", name=str)
    M2 = _make_model("dogs", name=str)

    M1(name="Whiskers").save()
    M2(name="Rex").save()

    assert len(M1.all()) == 1
    assert len(M2.all()) == 1
    assert M1.find(1).name == "Whiskers"
    assert M2.find(1).name == "Rex"
