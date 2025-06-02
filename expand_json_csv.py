import csv
import json
import re
import os

input_file = 'audit-inputs/59-usap-recrawl.csv'
output_file = os.path.join("audit-outputs", os.path.splitext(os.path.basename(input_file))[0] + "-expanded.csv")
json_col = 'Gemini: JSON Schema'

def extract_json(text):
    if not text:
        return {}
    match = re.search(r'```json\s*({.*})\s*```', text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        json_str = text
    try:
        return json.loads(json_str)
    except Exception:
        return {}

with open(input_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    all_keys = set()
    for row in rows:
        js = extract_json(row.get(json_col, ''))
        all_keys.update(js.keys())

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    # fieldnames = reader.fieldnames + [k for k in all_keys if k not in reader.fieldnames]
    fieldnames = [fn for fn in reader.fieldnames if fn != json_col] + [k for k in all_keys if k not in reader.fieldnames]

    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        
        js = extract_json(row.get(json_col, ''))
        for k in all_keys:
            row[k] = js.get(k, '')
        del row[json_col]
        writer.writerow(row)



print(f"Expanded CSV written to {output_file}")
