import polars as pl
from .header_cleaner import clean_header

def filter_html_rows(input_file, output_file):
    """
    Filter rows in a CSV file where the 'content_type' column contains 'text/html'.
    :param input_file: Path to the input CSV file.
    :param output_file: Path to the output CSV file.
    :return: Path to the output CSV file with filtered rows.
    """
    # Read CSV with proper handling of "None" values and ensuring HTTP Version is a string
    df = pl.read_csv(
        input_file,
        null_values=["None", "null", "NA", "N/A", ""],
        schema_overrides={"HTTP Version": pl.Utf8}  # Ensure HTTP Version is always read as string
    )
    # Clean column names to match the cleaned headers
    df.columns = [clean_header(col) for col in df.columns]
    # Filter rows where content_type contains 'text/html'
    filtered_df = df.filter(df['content_type'].str.contains('text/html'))
    filtered_df.write_csv(output_file)
    return output_file
