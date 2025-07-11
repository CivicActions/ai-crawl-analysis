from pathlib import Path
import polars as pl
import logging
from io import StringIO
from ai_crawl_analysis.utilities.json_cleaner import clean_json_file
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

def group_migration_paths(analysis_output: str | Path) -> Dict[str, Any]:
    """
    Group migration paths by the 'migration_group' column.

    Args:
        analysis_output (str | Path): Path to cleaned JSON file containing migration path data.

    Returns:
        dict: {
            "all_data": Polars DataFrame,
            "grouped_summary": Summary DataFrame (group, count),
            "groups": Dict[str, Polars DataFrame]
        }
    """
    cleaned_json = clean_json_file(str(analysis_output))
    df = pl.read_json(StringIO(cleaned_json))
    # Count total URLs
    grouped = df.group_by("migration_group").agg(pl.len().alias("url_count"))
    logging.info("\nMigration Groups Summary:\n%s", grouped)

    groups_dict = {
        group: df.filter(pl.col("migration_group") == group)
        for group in df["migration_group"].unique().to_list()
    }



    return {
        "all_data": df,
        "grouped_summary": grouped,
        "groups": groups_dict
    }

def _sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name)

def export_migration_groups(result: Dict[str, Any], output_dir: str | Path) -> None:
    """
    Export migration groups to CSV and JSON files.

    Args:
        result (dict): Dictionary from group_migration_paths()
        output_dir (str | Path): Directory to save the output files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    # Empty the output directory if it exists
    for file in output_dir.glob("*"):
        try:
            file.unlink()
            logging.info(f"Deleted existing file: {file}")
        except Exception as e:
            logging.warning(f"Could not delete {file}: {e}")

    # Save grouped summary
    summary_path = output_dir / "summary.csv"
    result["grouped_summary"].write_csv(summary_path)
    logging.info(f"Summary saved to {summary_path}")

    # Save complete dataset
    json_path = output_dir / "all_data.json"
    result["all_data"].write_json(json_path)
    logging.info(f"Complete dataset saved to {json_path}")

    # Export all data sorted by group
    all_sorted = result["all_data"].sort("migration_group")
    sorted_csv_path = output_dir / "all_data_by_group.csv"
    all_sorted.write_csv(sorted_csv_path)
    logging.info(f"All data sorted by migration group saved to {sorted_csv_path}")

    # Export each group
    for group_name, df_group in result["groups"].items():
        safe_name = _sanitize_filename(group_name)
        file_path = output_dir / f"{safe_name}.csv"
        df_group.write_csv(file_path)
        logging.info(f"Group '{group_name}' saved to {file_path}")

if __name__ == "__main__":
    analysis_output_path = Path("data/crawl-analysis/migration_groups.json")
    output_dir = Path("data/migration_groups")

    result = group_migration_paths(analysis_output_path)
    export_migration_groups(result, output_dir)

    logging.info(f"\nGrouped migration paths from {analysis_output_path}")
    logging.info(f"All groups exported to {output_dir}")
