import polars
from ai_migrations.utilities.ai_call import call_ai

# Given a CSV file, extract some columns and write them to a new CSV file.
def extract_descriptive_cols(input_csv: str, output_csv: str, columns: list):
    """
    Extract specified columns from a CSV file and write them to a new CSV file.
    
    :param input_csv: Path to the input CSV file.
    :param output_csv: Path to the output CSV file.
    :param columns: List of column names to extract.
    """
    # Read the input CSV file
    df = polars.read_csv(input_csv)
    
    # Select the specified columns
    selected_df = df.select(columns)
    
    # Write the selected columns to the output CSV file
    selected_df.write_csv(output_csv)

    return output_csv

# This script extracts specified columns from a CSV file and writes them to a new CSV file.
# It uses the Polars library for efficient data manipulation.

# Example usage
if __name__ == "__main__":
    input_file = 'data/audit-outputs/sample-seed-fund-expanded.csv'  # Change this to your input CSV file
    output_file = 'data/audit-outputs/extracted_columns.csv'  # Change this to your desired output CSV file
    columns_to_extract = ['address','page_description', 'page_structure', 'sidebar', 'sidebar_has_menu']  # Specify the columns you want to extract

    new_csv = extract_descriptive_cols(input_file, output_file, columns_to_extract)
    print(f"Extracted columns {columns_to_extract} from {input_file} to {output_file}")
    print(f"New CSV file created: {new_csv}")

    prompt = """
    Review the items in the Address column and use information in
    all columns to return suggestions about sections of this site that can be migrated 
    together or treated as the same page or content type. Ignore non-HTML pages. Also return the
    input CSV with an additional column called 'migration_group' that contains a suggested migration group for each row.
    The migration group should be a short descriptive name that indicates the content type or purpose of the page.
    For example, if the page is a blog post, the migration group could be 'Blog Post'.
    """
    response = call_ai(prompt, new_csv, model="gemini-2.0-flash-lite", temperature=0.5)
    print("AI Response:", response)

