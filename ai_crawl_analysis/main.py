"""
Main module that orchestrates the AI migrations processing pipeline.

This script coordinates the execution of the entire data processing pipeline:
1. Expand JSON columns in a CSV file: expand_json_csv.py
2. Filter HTML rows and clean data
3. Analyze crawl data and extract descriptive columns: crawl_analysis.py
4. Group data by migration paths: grouped_migration_paths.py

Usage:
    python -m ai_crawl_analysis.main input_file
    
Example:
    python -m ai_crawl_analysis.main data/audit-inputs/sample-seed-fund.csv
"""

import argparse
import sys
import os
from pathlib import Path
import logging

# Import processing modules
from ai_crawl_analysis.expand_json_csv import expand_json_csv
from ai_crawl_analysis.crawl_analysis import crawl_analysis
from ai_crawl_analysis.grouped_migration_paths import group_migration_paths, export_migration_groups

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    """
    Orchestrates the execution of the AI migrations processing pipeline.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process crawled site data for AI-assisted migration.")
    parser.add_argument("input_file", help="Path to the input CSV file with crawled data")
    parser.add_argument("--skip-steps", type=int, default=0, help="Skip the first N processing steps. There are 3 steps in total. --skip-steps=2 will skip the first two steps and only run the third step.")
    parser.add_argument("--output-dir", default="data", help="Base output directory for all generated files")
    args = parser.parse_args()
    
    # Resolve input file path
    input_file = Path(args.input_file)
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        sys.exit(1)
    
    # Create output directories if they don't exist
    output_base = Path(args.output_dir)
    audit_outputs_dir = output_base / "audit-outputs"
    crawl_analysis_dir = output_base / "crawl-analysis"
    migration_groups_dir = output_base / "migration_groups"
    
    for directory in [audit_outputs_dir, crawl_analysis_dir, migration_groups_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Get the base name of the input file for naming outputs
    input_name = input_file.stem
    
    # STEP 1: Expand JSON columns in the CSV file
    if args.skip_steps < 1:
        logger.info("Step 1: Expanding JSON columns in CSV")
        expanded_csv = audit_outputs_dir / f"{input_name}-expanded.csv"
        try:
            expand_json_csv(input_file, expanded_csv)
            logger.info(f"Expanded CSV saved to: {expanded_csv}")
        except Exception as e:
            logger.error(f"Error during Step 1 (expand_json_csv): {e}")
            sys.exit(1)
    else:
        expanded_csv = audit_outputs_dir / f"{input_name}-expanded.csv"
        if not expanded_csv.exists():
            logger.error(f"Expanded CSV not found: {expanded_csv}")
            sys.exit(1)
        logger.info(f"Skipped step 1, using existing file: {expanded_csv}")
    
    # STEP 2: Analyze crawl data and extract descriptive columns
    if args.skip_steps < 2:
        logger.info("Step 2: Analyzing crawl data")
        extracted_columns_file = audit_outputs_dir / "extracted_columns.json"
        columns_to_extract = ['address', 'page_description', 'page_structure', 'sidebar', 'sidebar_has_menu']
        
        crawl_analysis(str(expanded_csv), str(extracted_columns_file), columns_to_extract)
        migration_groups_path = crawl_analysis_dir / "final-analysis-output.json"
        logger.info(f"Crawl analysis completed, migration groups saved to: {migration_groups_path}")
    else:
        migration_groups_path = crawl_analysis_dir / "final-analysis-output.json"
        if not migration_groups_path.exists():
            logger.error(f"Migration groups file not found: {migration_groups_path}")
            sys.exit(1)
        logger.info(f"Skipped step 2, using existing file: {migration_groups_path}")
    
    # STEP 3: Group data by migration paths
    if args.skip_steps < 3:
        logger.info("Step 3: Grouping data by migration paths")
        result = group_migration_paths(migration_groups_path)
        export_migration_groups(result, migration_groups_dir)
        logger.info(f"Migration paths grouped and exported to: {migration_groups_dir}")
    else:
        logger.info(f"Skipped step 3, using existing files in: {migration_groups_dir}")
    
    logger.info("Processing pipeline completed successfully.")

if __name__ == "__main__":
    main()
