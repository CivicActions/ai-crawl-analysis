import ast
import csv
from typing import List, Set


def get_deduplicated_items_from_column(
    csv_filename: str, column_name: str
) -> List[str]:
    """
    Reads a CSV file, extracts all values from the specified column, parses Python-style list strings,
    and returns a deduplicated list of items (stripped of whitespace).
    """
    items: Set[str] = set()
    with open(csv_filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            value = row.get(column_name, "")
            if value:
                try:
                    # Try to parse as a Python list
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, list):
                        for item in parsed:
                            cleaned = str(item).strip()
                            if cleaned:
                                items.add(cleaned)
                    else:
                        # Fallback: treat as a single string
                        cleaned = str(parsed).strip()
                        if cleaned:
                            items.add(cleaned)
                except Exception:
                    # Fallback: treat as a comma-separated string
                    for item in value.split(","):
                        cleaned = item.strip().strip("'\"")
                        if cleaned:
                            items.add(cleaned)
    return sorted(items)


# Example usage:
if __name__ == "__main__":
    # Change the filename and column as needed
    csv_file = "data/audit-outputs/sample-seed-fund-expanded.csv"
    column = "js_libraries"
    result = get_deduplicated_items_from_column(csv_file, column)
    print(f"Deduplicated items in '{column}':")
    for item in result:
        print(item)
