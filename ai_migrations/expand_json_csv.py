import csv
import json
import re
import os

# === CONFIGURATION ===
input_file = 'data/audit-inputs/sample-seed-fund.csv'  # Change this to the downloaded CSV file.
json_col = 'Gemini: JSON schema'

input_name = os.path.splitext(os.path.basename(input_file))[0]
output_file = os.path.join('data/audit-outputs', f"{input_name}-expanded.csv")

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
    lowercase_headers = [h.lower() for h in reader.fieldnames]

    if json_col.lower() not in lowercase_headers:
        print(f"❌ Column '{json_col}' not found in CSV. Available columns:\n{reader.fieldnames}")
        exit(1)

    # Collect all keys across all JSON objects
    json_keys = set()
    for row in rows:
        js = extract_json(row.get(json_col, ''))
        if isinstance(js, dict):
            for k in js.keys():
                # Avoid overwriting existing CSV fields
                if k not in reader.fieldnames:
                    json_keys.add(k)

# === Write Expanded CSV ===
fieldnames = [f for f in reader.fieldnames if f != json_col] + sorted(json_keys)

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for row in rows:
        js = extract_json(row.get(json_col, ''))
        expanded = {k: js.get(k, '') for k in json_keys} if isinstance(js, dict) else {}
        # Don't modify original row dict directly
        clean_row = {k: row.get(k, '') for k in fieldnames if k not in json_keys}
        clean_row.update(expanded)
        writer.writerow(clean_row)

print(f"✅ Expanded CSV written to: {output_file}")

