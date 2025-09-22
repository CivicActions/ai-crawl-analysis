"""
Utility for cleaning and processing JSON files with malformed content.
This cleans JSON files that may contain:
- Code fences (```json ... ```)
- Extraneous text before/after JSON
- Incomplete or cut-off objects at the end
- Malformed JSON structure
"""

import json
from pathlib import Path


def clean_json_file(file_path: str | Path, expected_keys: int = 6) -> str:
    """
    Clean a JSON file by:
    1. Removing code fences (```json and ```)
    2. Extracting only the JSON array content
    3. Removing incomplete objects from the end
    4. Ensuring the file is properly closed

    Parameters:
        file_path (str | Path): The path to the JSON file to clean
        expected_keys (int): Expected number of non-null keys each object should have

    Returns:
        str: The cleaned JSON content
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # Step 1: Read the file
    content = file_path.read_text(encoding="utf-8")

    # Step 2: Remove code fences
    content = remove_code_fences(content)

    # Step 3: Extract JSON content (find JSON array/object)
    content = extract_json_content(content)

    # Ensure we have a JSON array specifically
    if not content.startswith("["):
        raise ValueError("No JSON array found in file")

    # Step 4: Try to parse and clean incomplete objects
    try:
        # If it parses successfully, check the last object
        data = json.loads(content)

        if isinstance(data, list) and data:
            last_object = data[-1]

            if isinstance(last_object, dict):
                non_null_keys = {k: v for k, v in last_object.items() if v is not None}

                if len(non_null_keys) < expected_keys:
                    data.pop()  # Remove incomplete last object

            # Convert back to clean JSON
            cleaned_json = json.dumps(data, indent=2, ensure_ascii=False)

        else:
            cleaned_json = content

    except json.JSONDecodeError:
        # Step 5: Handle malformed JSON by finding the last complete object
        lines = content.strip().split("\n")

        # Work backwards to find a valid structure
        for i in range(len(lines) - 1, -1, -1):
            test_content = "\n".join(lines[:i]).strip()

            # Try to create valid JSON
            if test_content.endswith("}"):
                test_content += "\n]"
            elif test_content.endswith(","):
                test_content = test_content.rstrip(",") + "\n]"
            else:
                continue

            try:
                test_data = json.loads(test_content)
                if isinstance(test_data, list) and test_data:
                    cleaned_json = json.dumps(test_data, indent=2, ensure_ascii=False)
                    break
            except json.JSONDecodeError:
                continue
        else:
            raise ValueError("Could not fix malformed JSON")

    # Step 6: Write the cleaned content back to the file
    file_path.write_text(cleaned_json, encoding="utf-8")

    return cleaned_json


def validate_json_file(file_path: str | Path, expected_keys: int = 6) -> bool:
    """
    Validate if a JSON file is complete and properly formatted.

    Parameters:
        file_path (str | Path): Path to the JSON file
        expected_keys (int): Expected number of non-null keys in each object

    Returns:
        bool: True if valid and complete, False otherwise
    """
    try:
        if isinstance(file_path, str):
            file_path = Path(file_path)

        content = file_path.read_text(encoding="utf-8")
        data = json.loads(content)

        if isinstance(data, list) and data:
            last_object = data[-1]
            if isinstance(last_object, dict):
                non_null_keys = {k: v for k, v in last_object.items() if v is not None}
                return len(non_null_keys) >= expected_keys

        return True
    except (json.JSONDecodeError, ValueError, FileNotFoundError):
        return False


def remove_code_fences(text: str) -> str:
    """
    Remove code fences from text content, typically returned from LLM responses.
    Code fences are Markdown formatting like ```json at the beginning and ``` at the end.

    Parameters:
        text (str): The text content that might contain code fences.

    Returns:
        str: The cleaned text without code fences.
    """
    cleaned_text = text.strip()

    # Remove starting code fence if present
    if cleaned_text.startswith("```json") or cleaned_text.startswith("```"):
        cleaned_text = (
            cleaned_text.split("\n", 1)[1] if "\n" in cleaned_text else cleaned_text
        )

    # Remove ending code fence if present
    if cleaned_text.endswith("```"):
        cleaned_text = (
            cleaned_text.rsplit("\n", 1)[0] if "\n" in cleaned_text else cleaned_text
        )

    return cleaned_text.strip()


def extract_json_content(text: str) -> str:
    """
    Extract JSON content from text, assuming it's already been cleaned of code fences.

    Parameters:
        text (str): Text that should contain JSON content.

    Returns:
        str: The JSON content or original text if no valid JSON structure found.
    """
    text = text.strip()

    # After removing code fences, the text should start with [ or {
    if text.startswith("[") or text.startswith("{"):
        return text

    # If not, try to find the first occurrence of [ or {
    start_pos = min(
        (text.find(char) for char in ["[", "{"] if text.find(char) != -1), default=-1
    )

    if start_pos != -1:
        return text[start_pos:]

    return text


if __name__ == "__main__":
    # Test the JSON cleaner with real files
    # Usage: python -m ai_crawl_analysis.utilities.json_cleaner data/crawl-analysis/migration_groups.json

    import argparse

    parser = argparse.ArgumentParser(
        description="Clean and validate JSON files with mixed content"
    )
    parser.add_argument("file", help="Path to the JSON file to clean")
    parser.add_argument(
        "--expected-keys",
        type=int,
        default=6,
        help="Expected number of non-null keys each object should have (default: 6)",
    )
    args = parser.parse_args()

    print(f"Processing file: {args.file}")
    print("=" * 50)

    try:
        # Clean the JSON file
        cleaned_content = clean_json_file(args.file, args.expected_keys)

        # Validate the result
        is_valid = validate_json_file(args.file, args.expected_keys)

        print("\n" + "=" * 50)
        print("RESULTS:")
        print("✅ File cleaned and saved successfully")
        print("✅ JSON is valid and complete: {'YES' if is_valid else 'NO'}")

        # Show a preview of the cleaned content
        if len(cleaned_content) > 300:
            print(f"\nPreview (first 300 chars):\n{cleaned_content[:300]}...")
        else:
            print(f"\nCleaned content:\n{cleaned_content}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("- Check if the file exists and is readable")
        print("- Ensure the file contains JSON or JSON-like content")
        print("- Look for common syntax errors like missing brackets or quotes")
