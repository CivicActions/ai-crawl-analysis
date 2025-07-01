"""
Call an AI model with a given prompt and return the response.

Parameters:
  :param prompt: The prompt to send to the AI model.
  :param system_instructions: Instructions to guide the AI model's behavior.
  :param file: Optional JSON file path to provide the data to process. Will accept just the text prompt if no file is provided.
  :param content: Optional JSON content as string to provide directly instead of reading from a file.
  :param model: The AI model to use (default is "gemini-2.5-pro-preview-06-05").
  :param temperature: The temperature for the model's response (default is 0.3).
  :return: The response from the AI model.

Usage:
  from ai_crawl_analysis.utilities.ai_call import call_ai
  # With file:
  response = call_ai(prompt=prompt, file=json_file_path)
  # With direct content:
  response = call_ai(prompt=prompt, content=json_content)

  Run directly to test: python run ai_crawl_analysis.utilities.ai_call OR uv run -m ai_crawl_analysis.utilities.ai_call
"""

from dotenv import load_dotenv
import os
from google import genai
from google.genai import types

API_KEY = 'GEMINI_API_KEY'
DEFAULT_SYSTEM_INSTRUCTIONS = "You are an AI assistant that provides insights based on the provided data."
DEFAULT_MODEL = "gemini-2.5-pro-preview-06-05"
DEFAULT_RESPONSE_SCHEMA = {"type": "object", "properties": {"insights": {"type": "string"}}}

def call_ai(
        prompt: str,
        file: str = None,
        content: str = None,
        system_instructions: str = DEFAULT_SYSTEM_INSTRUCTIONS,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.3,
        response_schema = DEFAULT_RESPONSE_SCHEMA
        ) -> str:

    if not prompt:
        raise ValueError("Prompt cannot be empty.")
    if not (0.0 <= temperature <= 1.0):
        raise ValueError("Temperature must be between 0.0 and 1.0.")
    
    # Load the API key from environment variables
    load_dotenv()
    api_key = os.getenv(API_KEY)

    if not api_key:
        raise ValueError("API key for the AI model is not set in environment variables.")

    # Initialize the AI client with the API key
    client = genai.Client(api_key=api_key)
    
    json_content = None
    
    # If direct content is provided, use it
    if content:
        json_content = content
    # If a file is provided, read its content
    elif file:
        # Check if it's a file path or actual JSON content
        if os.path.exists(file) and file.lower().endswith('.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    json_content = f.read()
            except FileNotFoundError:
                raise FileNotFoundError(f"The file '{file}' was not found.")
            except Exception as e:
                raise Exception(f"Error reading the JSON file: {str(e)}")
        else:
            # Assume it's direct JSON content
            json_content = file

    # Generate content using the specified model and prompt.
    response = client.models.generate_content(
        model=model,
        contents=[json_content, prompt] if json_content else prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instructions,
            response_schema=response_schema
        )
    )
    # Return the text response from the AI model.
    return response.text

if __name__ == "__main__":
    # Example usage
    prompt = "Analyze the data in this JSON file and provide insights."
    file = "data/audit-outputs/extracted_columns.json"  # Change this to your input JSON file
    response = call_ai(prompt=prompt, file=file)
    print("\nAI Response:", response)
