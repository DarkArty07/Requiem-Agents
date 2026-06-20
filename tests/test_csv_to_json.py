import pytest
import json
import csv
import tempfile
import os
from pathlib import Path

# Import the function to test
from requiem.csv_tools import csv_to_json


class TestCsvToJson:
    """Tests for csv_to_json function."""

    def test_basic_conversion(self, tmp_path):
        """Test basic CSV to JSON conversion with headers and data rows."""
        csv_content = "name,age,city\nAlice,30,New York\nBob,25,Los Angeles\nCharlie,35,Chicago"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        json_file = tmp_path / "output.json"

        result = csv_to_json(str(csv_file), str(json_file))

        assert result == 3  # number of data rows

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) == 3

        expected = [
            {"name": "Alice", "age": "30", "city": "New York"},
            {"name": "Bob", "age": "25", "city": "Los Angeles"},
            {"name": "Charlie", "age": "35", "city": "Chicago"},
        ]
        assert data == expected

    def test_different_delimiter(self, tmp_path):
        """Test CSV with semicolon delimiter."""
        csv_content = "name;age;city\nAlice;30;New York\nBob;25;Los Angeles"
        csv_file = tmp_path / "test_semicolon.csv"
        csv_file.write_text(csv_content)
        json_file = tmp_path / "output_semicolon.json"

        result = csv_to_json(str(csv_file), str(json_file), delimiter=";")

        assert result == 2

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        expected = [
            {"name": "Alice", "age": "30", "city": "New York"},
            {"name": "Bob", "age": "25", "city": "Los Angeles"},
        ]
        assert data == expected

    def test_empty_csv_only_headers(self, tmp_path):
        """Test CSV with only headers and no data rows raises ValueError."""
        csv_content = "name,age,city"
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text(csv_content)
        json_file = tmp_path / "output_empty.json"

        with pytest.raises(ValueError, match="CSV file has no data rows"):
            csv_to_json(str(csv_file), str(json_file))

    def test_file_not_found(self, tmp_path):
        """Test that a nonexistent CSV path raises FileNotFoundError."""
        json_file = tmp_path / "output_notfound.json"

        with pytest.raises(FileNotFoundError):
            csv_to_json("/nonexistent/file.csv", str(json_file))

    def test_quoted_fields_with_commas(self, tmp_path):
        """Test CSV with quoted fields containing commas."""
        csv_content = 'name,age,city\nJohn,"Doe, Jr.",30\nJane,"Smith, Sr.",25'
        csv_file = tmp_path / "quoted.csv"
        csv_file.write_text(csv_content)
        json_file = tmp_path / "output_quoted.json"

        result = csv_to_json(str(csv_file), str(json_file))

        assert result == 2

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        expected = [
            {"name": "John", "age": "Doe, Jr.", "city": "30"},
            {"name": "Jane", "age": "Smith, Sr.", "city": "25"},
        ]
        assert data == expected

    def test_utf8_special_characters(self, tmp_path):
        """Test UTF-8 encoding with special characters (tildes, eñes)."""
        csv_content = "name,description\nJosé,Música\nMaría,Piñón\nÉlida,Canción"
        csv_file = tmp_path / "utf8.csv"
        csv_file.write_text(csv_content, encoding="utf-8")
        json_file = tmp_path / "output_utf8.json"

        result = csv_to_json(str(csv_file), str(json_file))

        assert result == 3

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        expected = [
            {"name": "José", "description": "Música"},
            {"name": "María", "description": "Piñón"},
            {"name": "Élida", "description": "Canción"},
        ]
        assert data == expected

    def test_utf8_with_uppercase_n_tilde(self, tmp_path):
        """Test UTF-8 encoding with uppercase Ñ character."""
        csv_content = "nombre,valor\nÑoño,100\nAna María,200"
        csv_file = tmp_path / "utf8_upper.csv"
        csv_file.write_text(csv_content, encoding="utf-8")
        json_file = tmp_path / "output_utf8_upper.json"

        result = csv_to_json(str(csv_file), str(json_file))

        assert result == 2

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        expected = [
            {"nombre": "Ñoño", "valor": "100"},
            {"nombre": "Ana María", "valor": "200"},
        ]
        assert data == expected
