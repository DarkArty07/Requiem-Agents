import csv


def csv_to_json(csv_path):
    """
    Read a CSV file and return its contents as a list of dictionaries.

    Uses csv.DictReader to parse the file. Each dictionary in the returned
    list represents one row, with keys taken from the CSV header row.

    Args:
        csv_path (str): Path to the CSV file to read.

    Returns:
        list[dict]: List of dictionaries representing the CSV data.

    Raises:
        FileNotFoundError: If the file at csv_path does not exist.
        Exception: For any other I/O or parsing errors.

    Example:
        >>> data = csv_to_json('data.csv')
        >>> print(data[0])
        {'name': 'Alice', 'age': '30', 'city': 'New York'}
    """
    try:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    except FileNotFoundError:
        raise
    except Exception as e:
        raise Exception(f"An error occurred while reading the CSV file: {e}") from e
