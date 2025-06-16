"""
Utility functions for cleaning and processing JSON data.
"""
from pathlib import Path

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
    Read a JSON file and clean it by removing any code fences.
    
    Parameters:
        file_path (str | Path): The path to the JSON file to read and clean.
        
    Returns:
        str: The cleaned JSON content without code fences.
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    # Read the file content with UTF-8 encoding
    content = file_path.read_text(encoding='utf-8')
    
    # Clean the content by removing code fences
    cleaned_content = remove_code_fences(content)
    
    return cleaned_content
