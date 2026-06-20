"""Mini ORM — lightweight SQLite-backed object-relational mapper.

Provides a Database singleton, a ModelMeta metaclass that auto-registers
models and creates tables, and a BaseModel with save/find/delete/all.
"""

import sqlite3
from typing import Any, ClassVar, Dict, List, Optional, Type, get_type_hints


# ── Database singleton ────────────────────────────────────────────────────────

class Database:
    """Singleton database connection manager backed by SQLite."""

    _connection: ClassVar[Optional[sqlite3.Connection]] = None

    @classmethod
    def connect(cls, path: str = ":memory:") -> sqlite3.Connection:
        """Return a shared connection, creating it on first call.

        Args:
            path: Path to the SQLite database file. Defaults to in-memory.

        Returns:
            The shared sqlite3.Connection instance.
        """
        if cls._connection is None:
            cls._connection = sqlite3.connect(path, check_same_thread=False)
            cls._connection.row_factory = sqlite3.Row
        return cls._connection

    @classmethod
    def reset(cls) -> None:
        """Close and clear the shared connection (useful for tests)."""
        if cls._connection is not None:
            cls._connection.close()
            cls._connection = None

    @classmethod
    def execute(cls, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a SQL statement.

        Args:
            sql: The SQL to execute.
            params: Parameters for the query.

        Returns:
            The cursor after execution.
        """
        conn = cls.connect()
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor

    @classmethod
    def fetchone(cls, sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Fetch a single row.

        Args:
            sql: The SELECT query.
            params: Parameters for the query.

        Returns:
            A sqlite3.Row or None.
        """
        conn = cls.connect()
        return conn.execute(sql, params).fetchone()

    @classmethod
    def fetchall(cls, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Fetch all matching rows.

        Args:
            sql: The SELECT query.
            params: Parameters for the query.

        Returns:
            A list of sqlite3.Row objects.
        """
        conn = cls.connect()
        return conn.execute(sql, params).fetchall()


# ── Type mapping ──────────────────────────────────────────────────────────────

_TYPE_MAP: Dict[type, str] = {
    int: "INTEGER",
    str: "TEXT",
    float: "REAL",
    bool: "INTEGER",
}


def _sql_type(py_type: type) -> str:
    """Map a Python type to its SQL column type.

    Args:
        py_type: A Python type (int, str, float, bool).

    Returns:
        The corresponding SQL type string.
    """
    return _TYPE_MAP.get(py_type, "TEXT")


# ── ModelMeta metaclass ───────────────────────────────────────────────────────

class ModelMeta(type):
    """Metaclass that auto-registers models and creates their SQL tables.

    Attributes:
        _models (Dict[str, Type]): Registry mapping table names to model classes.
    """

    _models: Dict[str, Type] = {}

    def __new__(
        mcs,
        name: str,
        bases: tuple,
        namespace: Dict[str, Any],
    ) -> "ModelMeta":
        cls = super().__new__(mcs, name, bases, namespace)

        # Register and create table if tablename is defined
        tablename: Optional[str] = namespace.get("__tablename__")
        if tablename is not None:
            ModelMeta._models[tablename] = cls
            _create_table(cls)

        return cls

    @classmethod
    def reset_registry(mcs) -> None:
        """Clear the model registry (useful for tests)."""
        mcs._models.clear()


def _get_fields(cls: Type) -> Dict[str, type]:
    """Extract field names and types from a model class annotations.

    Excludes attributes starting with '_' and 'id' (auto-generated).

    Args:
        cls: The model class.

    Returns:
        A dict mapping field names to their Python types.
    """
    hints = get_type_hints(cls)
    return {
        name: py_type
        for name, py_type in hints.items()
        if not name.startswith("_") and name != "id"
    }


def _create_table(cls: Type) -> None:
    """Create the SQLite table for a model class if it doesn't exist.

    Args:
        cls: The model class.
    """
    fields = _get_fields(cls)
    columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
    for field_name, py_type in fields.items():
        columns.append(f"{field_name} {_sql_type(py_type)}")

    sql = f"CREATE TABLE IF NOT EXISTS {cls.__tablename__} ({', '.join(columns)})"
    Database.execute(sql)


# ── BaseModel ─────────────────────────────────────────────────────────────────

class BaseModel(metaclass=ModelMeta):
    """Base class for ORM models providing save/find/delete/all operations.

    Subclasses must define ``__tablename__`` and annotate their fields::

        class User(BaseModel):
            __tablename__ = "users"
            name: str
            email: str
    """

    __tablename__: ClassVar[str]

    def __init__(self, **kwargs: Any) -> None:
        """Initialize model instance with keyword arguments.

        Args:
            **kwargs: Field values keyed by name. 'id' is optional.
        """
        self.id: Optional[int] = kwargs.pop("id", None)

        # Set declared fields from kwargs or default to None
        for field_name in _get_fields(type(self)):
            setattr(self, field_name, kwargs.pop(field_name, None))

        # Capture any undeclared kwargs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self) -> None:
        """Persist the instance to the database.

        Performs INSERT if self.id is None, otherwise UPDATE.
        After INSERT, self.id is set to the new row id.
        """
        fields = _get_fields(type(self))
        field_names = list(fields.keys())
        values = [getattr(self, f) for f in field_names]

        if self.id is None:
            # INSERT
            placeholders = ", ".join(["?"] * len(field_names))
            columns = ", ".join(field_names)
            sql = (
                f"INSERT INTO {self.__tablename__} ({columns}) "
                f"VALUES ({placeholders})"
            )
            cursor = Database.execute(sql, tuple(values))
            self.id = cursor.lastrowid
        else:
            # UPDATE
            set_clause = ", ".join(f"{f} = ?" for f in field_names)
            sql = f"UPDATE {self.__tablename__} SET {set_clause} WHERE id = ?"
            Database.execute(sql, tuple(values) + (self.id,))

    def delete(self) -> None:
        """Delete this instance from the database.

        Raises:
            ValueError: If self.id is None (instance not yet saved).
        """
        if self.id is None:
            raise ValueError("Cannot delete an instance with no id (not saved)")
        sql = f"DELETE FROM {self.__tablename__} WHERE id = ?"
        Database.execute(sql, (self.id,))

    @classmethod
    def find(cls, id: int) -> Optional["BaseModel"]:
        """Find a single record by its primary key.

        Args:
            id: The primary key to look up.

        Returns:
            An instance of the model or None if not found.
        """
        sql = f"SELECT * FROM {cls.__tablename__} WHERE id = ?"
        row = Database.fetchone(sql, (id,))
        if row is None:
            return None
        return cls(**dict(row))

    @classmethod
    def all(cls) -> List["BaseModel"]:
        """Return all records from the table.

        Returns:
            A list of model instances.
        """
        sql = f"SELECT * FROM {cls.__tablename__}"
        rows = Database.fetchall(sql)
        return [cls(**dict(r)) for r in rows]

    def __repr__(self) -> str:
        """Return a readable representation including tablename and id.

        Returns:
            A string like ``User(id=3)``.
        """
        return f"{type(self).__name__}(id={self.id})"
