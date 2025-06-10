from dotenv import load_dotenv
import os
from google import genai
from google.genai import types

load_dotenv()

def call_ai(prompt: str, file: str, model: str = "gemini", temperature: float = 0.7) -> str:
    """
    Call an AI model with a given prompt and return the response.
    
    :param prompt: The prompt to send to the AI model.
    :param model: The AI model to use (default is "gemini").
    :param temperature: The temperature for the model's response (default is 0.7).
    :return: The response from the AI model.
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty.")
    if model not in ["gemini-2.0-flash-lite", "gpt-3.5-turbo", "gpt-4"]:
        raise ValueError("Unsupported model. Supported models are: gemini-2.0-flash-lite, gpt-3.5-turbo, gpt-4.")
    if not (0.0 <= temperature <= 1.0):
        raise ValueError("Temperature must be between 0.0 and 1.0.")
    
    # Load the API key from environment variables
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("API key for the AI model is not set in environment variables.")

    # Initialize the AI client with the API key
    client = genai.Client(api_key=api_key)
    # If a file is provided, confirm that it is a csv file and read its content
    if file:
        if not file.lower().endswith('.csv'):
            raise ValueError("Only CSV files are supported for analysis.")
        
        try:
            with open(file, 'r', encoding='utf-8') as f:
                csv_content = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{file}' was not found.")
        except Exception as e:
            raise Exception(f"Error reading the CSV file: {str(e)}")

    # Generate content using the specified model and prompt.
    response = client.models.generate_content(
        model=model,
        contents=[csv_content, prompt] if file else prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
        )
    )
    # Return the text response from the AI model.
    return response.text

if __name__ == "__main__":
    # Example usage
    prompt = "Analyze the data in this CSV file and provide insights."
    file = "data/audit-outputs/sample-seed-fund-expanded.csv"  # Change this to your input CSV file
    response = call_ai(prompt, file, model="gemini", temperature=0.5)
    print("\nAI Response:", response)
# Note: Ensure that the GEMINI_API_KEY environment variable is set before running this script.
