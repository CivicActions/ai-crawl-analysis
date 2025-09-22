"""
Streamlit UI app for uploading and downloading analysis files.

This app allows users to upload a CSV file, process it to expand JSON columns,
and download the results. It provides a simple interface for users to interact with the AI Migrations
analysis pipeline.

Usage:
  python -m streamlit run ai_crawl_analysis/app.py

"""

import os
import tempfile
import zipfile

import streamlit as st

from ai_crawl_analysis.crawl_analysis import crawl_analysis

# Import processing modules
from ai_crawl_analysis.expand_json_csv import expand_json_csv
from ai_crawl_analysis.grouped_migration_paths import (
    export_migration_groups,
    group_migration_paths,
)
from ai_crawl_analysis.utilities.create_output_dirs import create_output_dirs


def expand_crawl_data(uploaded_file, expanded_csv, status):
    """
    Process the uploaded CSV file to expand JSON columns and save the result.

    Args:
        uploaded_file: The uploaded CSV file from Streamlit.
        expanded_csv: Path to save the expanded CSV file.
        status: Streamlit status object to update UI.
    """
    try:
        # Create a temporary file to save the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            # Write the uploaded file content to a temporary file
            uploaded_file.seek(0)  # Reset file pointer to beginning
            tmp.write(uploaded_file.getvalue())
            temp_path = tmp.name
        status.write("Expanding JSON columns in the uploaded CSV file...")
        expand_json_csv(temp_path, expanded_csv)

        # Clean up the temporary file
        os.unlink(temp_path)

        status.write("✅ JSON Columns expanded successfully.")
        return expanded_csv
    except Exception as e:
        status.write(f"❌ Error during processing: {e}")
        st.error(f"Error processing file: {e}")
        st.stop()


def main():
    """
    Main function to run the Streamlit app.
    """
    # Streamlit reruns the script on every interaction, so we need to ensure
    # that the session states are tracked for each processing step.
    if "crawl_analysis_complete" not in st.session_state:
        st.session_state.crawl_analysis_complete = False
    if "csv_expansion_complete" not in st.session_state:
        st.session_state.csv_expansion_complete = False
    if "migration_groups_complete" not in st.session_state:
        st.session_state.migration_groups_complete = False

    # Config options for the Streamlit app.
    st.set_page_config(
        page_title="AI-enhanced site crawl analyzer",
        page_icon=":robot_face:",
        layout="centered",
    )

    st.title(":sparkles: AI-enhanced site crawl analyzer")
    st.html(
        "<p style = 'font-size: 1.2rem'>This app allows you to upload a CSV file containing crawled "
        "site data, process it to expand JSON columns, analyze the crawl data, and return suggestions for "
        "grouping migration paths into content types.</p>"
    )

    # File uploader for the input CSV file
    uploaded_file = st.file_uploader(
        "Upload a CSV file of crawled site data", type="csv"
    )

    if uploaded_file is not None:
        uploaded_file_name = uploaded_file.name
        audit_outputs_dir, crawl_analysis_dir, migration_groups_dir = (
            create_output_dirs()
        )

    else:
        st.warning("Please upload a CSV file to proceed.")
        # Reset session states when no file is uploaded or if a previous upload was deleted.
        st.session_state.crawl_analysis_complete = False
        st.session_state.csv_expansion_complete = False
        st.session_state.migration_groups_complete = False
        st.stop()

    expanded_csv = audit_outputs_dir / f"{uploaded_file_name}-expanded.csv"

    # Trigger the file expansion and download expanded CSV.
    status = st.status(
        f"Processing {uploaded_file_name}...", expanded=True, state="running"
    )
    if not st.session_state.csv_expansion_complete:
        expand_crawl_data(uploaded_file, expanded_csv, status)
        st.session_state.csv_expansion_complete = True
    else:
        status.update(
            label=f"Using existing expanded file: {expanded_csv.name}",
            expanded=False,
            state="complete",
        )
    # Provide a download button for the expanded CSV file
    with open(expanded_csv, "rb") as f:
        st.download_button(
            label="Download the expanded CSV file",
            data=f,
            file_name=f"{uploaded_file_name}-expanded.csv",
            mime="text/csv",
            icon=":material/download:",
            type="primary",
        )
    status.update(
        label=f"✅ {uploaded_file_name} has been expanded into {expanded_csv.name}.",
        expanded=False,
        state="complete",
    )

    # STEP 2: Analyze crawl data and extract descriptive columns
    status = st.status(
        "Analyzing crawl data... (This can take a while depending on the size of the data)",
        expanded=True,
        state="running",
    )

    extracted_columns_file = audit_outputs_dir / "extracted_columns.json"
    columns_to_extract = [
        "address",
        "page_description",
        "page_structure",
        "sidebar",
        "sidebar_has_menu",
    ]
    crawl_analysis_output = None

    if (
        not st.session_state.crawl_analysis_complete
        and expanded_csv.exists()
        and expanded_csv.stat().st_size > 0
    ):
        crawl_analysis(
            str(expanded_csv), str(extracted_columns_file), columns_to_extract, True
        )
        st.session_state.crawl_analysis_complete = True
        crawl_analysis_output = crawl_analysis_dir / "final-analysis-output.json"
        status.update(
            label="✅ Crawl analysis completed.", expanded=False, state="complete"
        )
    elif st.session_state.crawl_analysis_complete:
        status.update(
            label="Using existing crawl analysis output",
            expanded=False,
            state="complete",
        )
        crawl_analysis_output = crawl_analysis_dir / "final-analysis-output.json"
    else:
        st.error(
            "Expanded CSV file not found. Please ensure the file was processed correctly."
        )
        st.stop()

    # STEP 3: Group data by migration paths
    # Only proceed if crawl_analysis has finished and migration_groups_path exists and is not empty
    if (
        crawl_analysis_output is not None
        and crawl_analysis_output.exists()
        and crawl_analysis_output.stat().st_size > 0
    ):
        status = st.status(
            "Sorting and grouping analyzed data by their identified migration groups...",
            expanded=True,
            state="running",
        )
        if not st.session_state.migration_groups_complete:
            result = group_migration_paths(crawl_analysis_output)
            export_migration_groups(result, migration_groups_dir)
            st.session_state.migration_groups_complete = True
            status.update(
                label="✅ URLs grouped by their identified migration groups for download.",
                expanded=False,
                state="complete",
            )
        else:
            status.update(
                label=f"Using existing migration groups output: {migration_groups_dir.name}",
                expanded=False,
                state="complete",
            )
    else:
        st.error(
            f"{crawl_analysis_output.name} does not exist or is empty, or crawl analysis step not "
            f"completed. Please check the crawl analysis step."
        )
        st.stop()

    # Add download section for migration group files
    st.divider()
    st.markdown("#### 📥 All Migration Group files")

    # Ensure migration_groups_dir exists and has files before attempting to create a zip
    if not migration_groups_dir.exists() or not any(migration_groups_dir.iterdir()):
        st.warning(
            "No migration group files found. Please ensure the previous steps were completed successfully."
        )
        return

    # Create a zip file of all migration group files
    zip_file_path = migration_groups_dir / "migration_groups.zip"
    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        for file in migration_groups_dir.iterdir():
            if file.is_file():
                zipf.write(file, arcname=file.name)

    # Add a download button for the zip file
    with open(zip_file_path, "rb") as f:
        st.download_button(
            label="Download a zipped file with all recommended migration groups",
            data=f,
            file_name="migration_groups.zip",
            mime="application/zip",
            icon=":material/download:",
        )

        st.text("\n")

        # Add individual file download section
        st.markdown("#### :file_folder: Individual Migration Group files")
        st.markdown(
            f"{len(list(migration_groups_dir.iterdir()))} files were created for {uploaded_file_name}. "
            f"You can download each file below:"
        )
        for file in migration_groups_dir.iterdir():
            if file.is_file():
                cols = st.columns([2, 1, 2])
                cols[0].write(file.name)
                cols[1].write("")  # Empty column for spacing
                with cols[2]:
                    with open(file, "rb") as f:
                        st.download_button(
                            label="Download",
                            data=f,
                            file_name=file.name,
                            mime="text/csv",
                            key=file.name,
                        )
    st.success(
        ":tada: All steps completed successfully! You can now download the processed files. :tada:"
    )


if __name__ == "__main__":
    main()
