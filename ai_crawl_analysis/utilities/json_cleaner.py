"""
Utility functions for cleaning and processing JSON data.
"""

from pathlib import Path
import json

def extract_json_content(text: str) -> str:
    """
    More robustly extract the first valid JSON block (array or object) from text.
    
    Parameters:
        text (str): Text that might contain JSON content mixed with other text.
        
    Returns:
        str: The extracted JSON content or the original text if no valid JSON is found.
    """
    decoder = json.JSONDecoder()
    text = text.lstrip()
    
    for i in range(len(text)):
        try:
            obj, end = decoder.raw_decode(text[i:])
            return text[i:i+end]
        except json.JSONDecodeError:
            continue
            
    return text  # fallback if nothing valid is found

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
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text.split('\n', 1)[1]  # Remove the first line
        
    # Remove ending code fence if present
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text.rsplit('\n', 1)[0]  # Remove the last line
        
    return cleaned_text

def read_and_clean_json_file(file_path: str | Path) -> str:
    """
    Read a JSON file and clean it by removing any code fences and extracting 
    only the actual JSON content even if there's additional text.
    
    Parameters:
        file_path (str | Path): The path to the JSON file to read and clean.
        
    Returns:
        str: The cleaned JSON content.
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    # Read the file content with UTF-8 encoding
    content = file_path.read_text(encoding='utf-8')
    
    # First clean the content by removing code fences
    content_without_fences = remove_code_fences(content)
    
    # Then extract only valid JSON content
    cleaned_json = extract_json_content(content_without_fences)
    print(cleaned_json[:200])  # Print first 200 characters for debugging
    
    return cleaned_json

def validate_json(content: str) -> bool:
    """
    Validate if a string contains valid JSON.
    
    Parameters:
        content (str): String content to validate as JSON
        
    Returns:
        bool: True if the content is valid JSON, False otherwise
    """
    try:
        json.loads(content)
        return True
    except json.JSONDecodeError:
        return False

if __name__ == "__main__":
    # Test with a sample problematic JSON file
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean and extract JSON from files with mixed content")
    parser.add_argument("file", help="Path to the JSON file to clean")
    args = parser.parse_args()
    
    cleaned_content = read_and_clean_json_file(args.file)
    
    print("==== Cleaned JSON Content ====")
    print(cleaned_content[:200] + "..." if len(cleaned_content) > 200 else cleaned_content)
    print("\n==== Validation ====")
    
    is_valid = validate_json(cleaned_content)
    print(f"Is valid JSON: {'✅ YES' if is_valid else '❌ NO'}")
    
    if not is_valid:
        print("\nTroubleshooting:")
        print("- Check if the file contains valid JSON structure")
        print("- Ensure JSON starts with '[' or '{' and ends with ']' or '}'")
        print("- Look for common syntax errors like missing commas or quotes")
