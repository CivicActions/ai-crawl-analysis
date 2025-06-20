"""
This script extracts specific columns from a CSV file containing site crawl data and writes them to a new JSON file.

Parameters:
  :param input_csv: Path to the input CSV file containing site crawl data.
  :param output_json: Path to the output JSON file where extracted columns will be saved.
  :param columns: List of column names to extract from the CSV file. 
  :return: Path to the output JSON file with the extracted columns.

Usage:
from ai_migrations.utilities.extract_cols_to_json import extract_cols_to_json

"""

import polars

def extract_cols_to_json(input_csv: str, output_json: str, columns: list):

    # Read the input CSV file with proper handling for "None" values and HTTP Version
    df = polars.read_csv(
        input_csv,
        null_values=["None", "null", "NA", "N/A", ""],
        schema_overrides={"HTTP Version": polars.Utf8}  # Ensure HTTP Version is always read as string
    )
    
    # Select the specified columns
    selected_df = df.select(columns)

    # Write the selected columns to the output JSON file
    selected_df.write_json(output_json)

    return output_json
