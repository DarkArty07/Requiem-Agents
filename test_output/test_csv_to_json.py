import pytest
import csv
from csv_to_json import csv_to_json


def test_csv_to_json_valid(tmp_path):
    """Test that csv_to_json correctly converts a valid CSV file with multiple rows."""
    csv_content = "name,age,city\nAlice,30,New York\nBob,25,Los Angeles\nCharlie,35,Chicago"
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)
    result = csv_to_json(str(csv_file))
    expected = [
        {"name": "Alice", "age": "30", "city": "New York"},
        {"name": "Bob", "age": "25", "city": "Los Angeles"},
        {"name": "Charlie", "age": "35", "city": "Chicago"},
    ]
    assert result == expected


def test_csv_to_json_file_not_found():
    """Test that csv_to_json raises FileNotFoundError for non-existent file."""
    with pytest.raises(FileNotFoundError):
        csv_to_json("/non/existent/file.csv")


def test_csv_to_json_empty(tmp_path):
    """Test that csv_to_json returns an empty list for header-only CSV."""
    csv_content = "name,age,city"
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text(csv_content)
    result = csv_to_json(str(csv_file))
    assert result == []
