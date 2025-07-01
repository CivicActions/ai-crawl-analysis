import polars as pl
import json

def csv_to_json(input_csv: str):
    """
    Convert a CSV file to a JSON file.

    :param input_csv: Path to the input CSV file.
    :return: Path to the output JSON file.
    """

    # Read the CSV file using Polars with proper handling for "None" values and HTTP Version
    df = pl.read_csv(
        input_csv,
        null_values=["None", "null", "NA", "N/A", ""],
        schema_overrides={"HTTP Version": pl.Utf8}  # Ensure HTTP Version is always read as string
    )

    # Convert the DataFrame to a list of dictionaries
    data = df.to_dicts()

    # Define the output JSON file path
    output_json = input_csv.replace('.csv', '.json')

    # Write the data to a JSON file
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    return output_json
