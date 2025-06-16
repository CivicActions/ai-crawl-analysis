"""
Groups migration paths based on the migration_group field using Polars.

This module processes a JSON file containing URL data with migration group classifications.
It groups the data by the migration_group column, calculates statistics, and exports
both a summary and individual CSV files for each group.

Parameters:
:param analysis_output: A JSON file with migration paths and their recommended migration groups
:return: Dictionary containing the full dataset, grouped summary, and individual dataframes for each group

Example:
    result = group_migration_paths('data/crawl-analysis/migration_groups.json')
    # Access the grouped summary
    summary = result["grouped_summary"]
    # Access a specific group's dataframe
    homepage_group = result["groups"]["Homepage"]
"""

from pathlib import Path
import polars as pl  # Use the common alias 'pl' for polars
import os
from io import StringIO
from ai_migrations.utilities.json_cleaner import read_and_clean_json_file

def group_migration_paths(analysis_output: str):
  """
  Group migration paths by migration_group column and provide statistics for each group.
  
  Parameters:
      analysis_output: Path to the JSON file containing the analysis output
      
  Returns:
      Dictionary containing the grouped dataframes and statistics
  """
  # Load and read the analysis output JSON file.
  cleaned_json = read_and_clean_json_file(analysis_output)
  
  # Parse the JSON into a Polars DataFrame
  df = pl.read_json(StringIO(cleaned_json))
  
  # Group by migration_group and compute statistics
  grouped = df.group_by("migration_group").agg([
      pl.len().alias("count")
  ])
  
  print(f"\nMigration Groups Summary:")
  print(grouped.select(["migration_group", "count"]))
  
  # Create a dictionary to store individual dataframes for each group
  groups_dict = {}
  
  # Create individual dataframes for each migration group
  for group_name in df["migration_group"].unique():
      group_df = df.filter(pl.col("migration_group") == group_name)
      groups_dict[group_name] = group_df
      
      # Print information about each group
      print(f"\n{group_name} - {len(group_df)} URLs")
      print(group_df.select("address").head(3))
      if len(group_df) > 3:
          print(f"... and {len(group_df) - 3} more URLs")
  
  return {
      "all_data": df,
      "grouped_summary": grouped,
      "groups": groups_dict
  }

def export_migration_groups(result, output_dir):
    """
    Export migration groups to individual CSV files and create a summary JSON.
    
    Parameters:
        result: Dictionary containing grouped data and statistics
        output_dir: Directory to save output files
    """
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export summary to CSV (this is safe as it doesn't contain nested data)
    result["grouped_summary"].write_csv(output_dir / "summary.csv")
    print(f"Summary saved to {output_dir / 'summary.csv'}")
    
    # Export full JSON with all data
    result["all_data"].write_json(output_dir / "all_data.json")
    print(f"Complete dataset saved to {output_dir / 'all_data.json'}")
    
    # Define scalar types that can be exported to CSV
    scalar_types = [pl.Boolean, pl.Utf8, pl.Float64, pl.Float32, pl.Int64, pl.Int32, pl.Int16, pl.Int8]
    
    # Create a combined dataframe with all data sorted by migration_group
    all_data_sorted = result["all_data"].sort("migration_group")
    
    # Export all data to a single CSV file, sorted by migration_group
    exportable_columns = [col for col in all_data_sorted.columns 
                         if any(isinstance(all_data_sorted[col].dtype, t) for t in scalar_types)]
    
    all_sorted_csv = output_dir / "all_data_by_group.csv"
    all_data_sorted.select(exportable_columns).write_csv(all_sorted_csv)
    print(f"All data sorted by migration group saved to {all_sorted_csv}")
    
    # Export each group to its own CSV file
    for group_name, group_df in result["groups"].items():
        # Create a safe filename by replacing problematic characters
        safe_name = "".join(c if c.isalnum() else "_" for c in group_name)
        output_file = output_dir / f"{safe_name}.csv"
        
        # Write to CSV - only export columns that are compatible with CSV
        exportable_columns = [col for col in group_df.columns 
                             if any(isinstance(group_df[col].dtype, t) for t in scalar_types)]
        
        group_df.select(exportable_columns).write_csv(output_file)
        print(f"Group '{group_name}' saved to {output_file}")

if __name__ == "__main__":
    # Example usage
    analysis_output_path = Path('data/crawl-analysis/migration_groups.json')
    output_dir = Path('data/migration_groups')
    
    result = group_migration_paths(analysis_output_path)
    
    # Export the results
    export_migration_groups(result, output_dir)
    
    print(f"\nGrouped migration paths from {analysis_output_path}")
    print(f"All groups exported to {output_dir}")
