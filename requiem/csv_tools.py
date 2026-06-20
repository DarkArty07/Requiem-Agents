import sys
from pathlib import Path

# Ensure src is on the path so we can import csv_to_json
_src_path = str(Path(__file__).resolve().parent.parent / "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

from csv_to_json import csv_to_json
