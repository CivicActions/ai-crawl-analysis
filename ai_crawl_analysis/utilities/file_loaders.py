"""
Utility functions for loading prompts and schema files.
"""

import json
from pathlib import Path

def file_loader(file_name, file_type='prompt'):
    current_file = Path(__file__).resolve()
    path = current_file.parent.parent.parent / 'prompts' / file_name

    if path.exists():
        try:
            if file_type == 'prompt':
                return path.read_text(encoding='utf-8').strip()
            elif file_type == 'schema':
                data = json.loads(path.read_text(encoding='utf-8'))
                return data.get("schema", {})
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading {file_type} from {path}: {e}")
    print(f"Warning: Could not load {file_type} from any location: {file_name}")
    return "" if file_type == 'prompt' else {}


def load_prompt(file_name:str):
    """
    Load prompt content from a text file in the prompts directory
    
    :param filename: Name of the text file in the prompts directory
    :return: The prompt content as a string
    """
    # Get the current script location and try both possible prompt paths
    return file_loader(file_name, file_type='prompt')

def load_schema(file_name:str):
    """
    Load schema content from a JSON file in the prompts directory
    
    :param filename: Name of the JSON file in the prompts directory
    :return: The schema content as a dictionary
    """
    # Get the current script location and try both possible schema paths
    return file_loader(file_name, file_type='schema')
