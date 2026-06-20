import csv
import json
import os


def csv_to_json(csv_path, json_path, delimiter=',', encoding='utf-8'):
    """
    Reads a CSV file and converts it to a JSON array of objects.

    The first row is used as headers. Each subsequent row becomes an object
    with headers as keys. Handles empty values, special characters, escaped
    quotes, and rows with inconsistent column counts.

    Args:
        csv_path (str): Path to the input CSV file.
        json_path (str): Path for the output JSON file.
        delimiter (str): CSV delimiter character. Defaults to ','.
        encoding (str): File encoding. Defaults to 'utf-8'.

    Returns:
        int: Number of data records converted (excluding header).

    Raises:
        FileNotFoundError: If csv_path does not exist.
        ValueError: If the CSV has only headers and no data rows.
        UnicodeDecodeError: If decoding the file with the given encoding fails.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    try:
        with open(csv_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)
    except UnicodeDecodeError:
        raise UnicodeDecodeError(
            encoding,
            b'',
            0,
            0,
            f"Failed to decode CSV file '{csv_path}' using encoding '{encoding}'."
        )

    if len(rows) < 2:
        raise ValueError(
            f"CSV file has no data rows: {csv_path}"
        )

    headers = rows[0]
    num_columns = len(headers)
    records = []

    for row in rows[1:]:
        obj = {}
        row_len = len(row)

        if row_len < num_columns:
            # Pad missing columns with empty strings
            padded_row = row + [''] * (num_columns - row_len)
        elif row_len > num_columns:
            # Truncate extra columns
            padded_row = row[:num_columns]
        else:
            padded_row = row

        for i in range(num_columns):
            val = padded_row[i].strip()
            obj[headers[i].strip()] = val

        records.append(obj)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    return len(records)
