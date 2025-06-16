"""
Expands JSON columns in a CSV file.

This module reads a CSV file, expands JSON data stored in a specified column,
adds new columns for each key in the JSON objects, and writes the expanded data to a new CSV file.

It also filters out non-HTML rows before processing.
"""

import csv
import json
import re
import os
from pathlib import Path
from ai_migrations.utilities.filter_html_rows import filter_html_rows
from ai_migrations.utilities.header_cleaner import clean_header

def extract_json(text):
    """
    Extract and parse JSON from text content.
    
    Args:
        text (str): Text that may contain JSON, possibly in code blocks
        
    Returns:
        dict: Parsed JSON object or empty dict if parsing fails
    """
    if not text:
        return {}

    text = text.strip()
    # Try to extract JSON from triple backticks, with or without 'json'
    match = re.search(r"```(?:json)?\s*({.*?})\s*```", text, re.DOTALL)
    json_str = match.group(1) if match else text

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        print(f"⚠️ Failed to parse JSON:\n{text[:200]}")
        return {}

def expand_json_csv(input_file, output_file, json_col='Gemini: JSON schema'):
    """
    Expand JSON columns in a CSV file.
    
    Args:
        input_file (str or Path): Path to the input CSV file
        output_file (str or Path): Path to the output expanded CSV file
        json_col (str): Name of the column containing JSON data to expand
        
    Returns:
        Path: Path to the expanded CSV file
    """
    input_file = Path(input_file)
    output_file = Path(output_file)
    
    # Create the parent directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Filter the input file and overwrite it with only text/html rows before further processing
    filtered_input_file = input_file.with_name(f"{input_file.name}.filtered.csv")
    filter_html_rows(str(input_file), str(filtered_input_file))
    
    # === Read and Parse CSV ===
    with open(filtered_input_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        # Clean headers
        original_headers = reader.fieldnames
        cleaned_headers = [clean_header(h) for h in original_headers]
        header_map = dict(zip(original_headers, cleaned_headers))

        # Clean the json_col name for matching
        json_col_clean = clean_header(json_col)
        lowercase_headers = [h.lower() for h in cleaned_headers]

        if json_col_clean.lower() not in lowercase_headers:
            print(f"❌ Column '{json_col}' not found in CSV. Available columns:\n{cleaned_headers}")
            return None
        
        # Find the actual column name with correct case (cleaned)
        actual_json_col = next((orig for orig, clean in header_map.items() if clean.lower() == json_col_clean.lower()), json_col)
        
        # Collect all keys across all JSON objects
        json_keys = set()
        for row in rows:
            js = extract_json(row.get(actual_json_col, ''))
            if isinstance(js, dict):
                for k in js.keys():
                    # Avoid overwriting existing CSV fields
                    if clean_header(k) not in cleaned_headers:
                        json_keys.add(clean_header(k))

    # === Write Expanded CSV ===
    fieldnames = [h for h in cleaned_headers if h != json_col_clean] + sorted(json_keys)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            js = extract_json(row.get(actual_json_col, ''))
            expanded = {clean_header(k): js.get(k, '') for k in json_keys} if isinstance(js, dict) else {}
            # Don't modify original row dict directly
            clean_row = {clean_header(k): row.get(k, '') for k in original_headers if clean_header(k) in fieldnames and clean_header(k) not in json_keys}
            clean_row.update(expanded)
            writer.writerow(clean_row)
    
    print(f"✅ Expanded CSV with {len(rows)} rows and {len(fieldnames)} columns written to {output_file}")
    print(f"✅ Added {len(json_keys)} new columns from JSON data: {', '.join(sorted(json_keys))}")
    return output_file

if __name__ == "__main__":
    # Example usage when running this script directly
    input_file = 'data/audit-inputs/sample-seed-fund.csv'
    input_name = Path(input_file).stem
    output_file = f'data/audit-outputs/{input_name}-expanded.csv'
    
    expand_json_csv(input_file, output_file)
