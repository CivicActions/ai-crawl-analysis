from pathlib import Path


def create_output_dirs():
    """
    Create necessary output directories for the application.

    Returns:
        tuple: Paths to the audit outputs, crawl analysis, and migration groups directories.
    """

    # Create the base directory if it doesn't exist
    audit_outputs_dir = Path("data/audit-outputs")
    audit_outputs_dir.mkdir(parents=True, exist_ok=True)

    crawl_analysis_dir = Path("data/crawl-analysis")
    crawl_analysis_dir.mkdir(parents=True, exist_ok=True)

    migration_groups_dir = Path("data/migration_groups")
    migration_groups_dir.mkdir(parents=True, exist_ok=True)

    return audit_outputs_dir, crawl_analysis_dir, migration_groups_dir
