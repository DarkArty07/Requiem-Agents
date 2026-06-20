"""Module providing CSV to JSON conversion functionality.

This module contains a function to read a CSV file and convert
its contents into a list of dictionaries using Python's csv.DictReader.
"""

import csv


def csv_to_json(csv_path):
    """Read a CSV file and return its contents as a list of dictionaries.

    Each dictionary in the returned list represents one row from the CSV,
    with the column headers from the first row as keys.

    Args:
        csv_path (str): The file path to the CSV file to read.

    Returns:
        list[dict]: A list of dictionaries, one per data row, using the
            CSV column headers as dictionary keys.

    Raises:
        FileNotFoundError: If the specified csv_path does not exist or is
            not a readable file.
    """
    try:
        with open(csv_path, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found at path: {csv_path}")
