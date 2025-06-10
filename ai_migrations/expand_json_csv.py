import csv
import json
import re
import os
from ai_migrations.utilities.filter_html_rows import filter_html_rows
from ai_migrations.utilities.header_cleaner import clean_header

# === CONFIGURATION ===
input_file = 'data/audit-inputs/sample-seed-fund.csv'  # Change this to the downloaded CSV file.
json_col = 'Gemini: JSON schema'

input_name = os.path.splitext(os.path.basename(input_file))[0]
output_file = os.path.join('data/audit-outputs', f"{input_name}-expanded.csv")

# Filter the input file and overwrite it with only text/html rows before further processing
filtered_input_file = input_file + '.filtered.csv'
filter_html_rows(input_file, filtered_input_file)
input_file = filtered_input_file

# === Extract the JSON objects from json_col ===
def extract_json(text):
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

# === Read and Parse CSV ===
with open(input_file, newline='', encoding='utf-8') as f:
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
        exit(1)
    
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

print(f"✅ Expanded CSV written to: {output_file}")
print(f"✅ Added {len(json_keys)} new columns from JSON data: {', '.join(sorted(json_keys))}")

