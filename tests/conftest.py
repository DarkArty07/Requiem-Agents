"""pytest fixtures for Requiem Agents tests."""

import os
import sys
import pytest
from pathlib import Path


@pytest.fixture
def temp_db(tmp_path):
    """Set REQUIEM_PROJECT_ROOT to a temp directory so tests don't touch the real state.db.

    Clears cached shared modules so they re-evaluate DB_PATH with the new root.
    Yields the temp DB path.
    """
    old_root = os.environ.get("REQUIEM_PROJECT_ROOT")
    os.environ["REQUIEM_PROJECT_ROOT"] = str(tmp_path)

    # Create the shared/ subdirectory so sqlite3.connect() can create the file
    (tmp_path / "shared").mkdir(parents=True, exist_ok=True)

    # Purge any previously cached shared modules so they see the new env var
    _purge_shared_modules()

    yield tmp_path / "shared" / "state.db"

    # Restore original env var
    if old_root is None:
        del os.environ["REQUIEM_PROJECT_ROOT"]
    else:
        os.environ["REQUIEM_PROJECT_ROOT"] = old_root

    # Restore modules
    _purge_shared_modules()


def _purge_shared_modules():
    """Remove 'shared' and 'shared.*' from sys.modules so next import picks up new env."""
    to_delete = [m for m in list(sys.modules) if m == "shared" or m.startswith("shared.")]
    for m in to_delete:
        del sys.modules[m]
