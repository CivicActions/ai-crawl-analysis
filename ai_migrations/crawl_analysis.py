import polars
from ai_migrations.utilities.ai_call import call_ai

# Given a CSV file, extract some columns and write them to a new CSV file.
def extract_descriptive_cols(input_csv: str, output_json: str, columns: list):
    """
    Extract specified columns from a CSV file and write them to a JSON.

    :param input_csv: Path to the input CSV file.
    :param output_csv: Path to the output CSV file.
    :param columns: List of column names to extract.
    """
    # Read the input CSV file
    df = polars.read_csv(input_csv)
    
    # Select the specified columns
    selected_df = df.select(columns)
    print(f"original count: {df.height}")
    print(f"filtered count: {selected_df.height}")

    # Write the selected columns to the output JSON file
    selected_df.write_json(output_json)

    return output_json


# Example usage
if __name__ == "__main__":
    input_file = 'data/audit-outputs/73_nairrpilot.org-expanded.csv'  # Change this to your input CSV file
    output_file = 'data/audit-outputs/extracted_columns.json'  # Change this to your desired output JSON file
    columns_to_extract = ['address','page_description', 'page_structure', 'sidebar', 'sidebar_has_menu']  # Specify the columns you want to extract

    new_json = extract_descriptive_cols(input_file, output_file, columns_to_extract)
    print(f"Extracted columns {columns_to_extract} from {input_file} to {output_file}")
    print(f"New JSON file created: {new_json}")

    prompt = """
      You are an expert in website structure analysis and content categorization.
      You are given a JSON file that contains site crawl data. The JSON includes a key titled "Address" that lists URLs from a website, along with additional metadata keys such as title, status code, content type, and others (if available).
      Your task is to:
      Analyze the Address key and use any supporting data in the other keys to understand the structure and content types across the website.
      Identify patterns or clusters of pages that represent the same type of content (e.g., blog posts, product pages, help articles, category pages, etc.).
      Assign each URL a migration group — a short, descriptive label (e.g., "Blog Post", "Product Page", "Help Article", "Landing Page") that represents the type of content or purpose of the page.
      Return all rows in the original JSON file, with an additional key called "migration_group" containing your suggested label for each row.
      Important guidelines:
      - The groupings should reflect how pages could be migrated or managed together in a CMS migration or site redesign.
      - Use consistent and human-readable group names.
      - Use URL patterns and metadata to infer groups.
      - Use the "page_description" and "page_structure" keys to help identify the content type.
      - Pages with the same layout or purpose should belong to the same group.
      - If you're uncertain about a specific URL, infer the most likely content type based on similar patterns in the dataset.
      Example output schema:
      {
      "address": "https://example.com/blog/how-to-use-our-product",
      "page_description": "A guide on using our product effectively.",
      "page_structure": "{'type': 'page', 'fields': [{'name': 'login_form', 'type': 'form', 'fields': [{'name': 'email', 'type': 'text'}, {'name': 'password', 'type': 'password'}, {'name': 'remember_me', 'type': 'checkbox'}]}, {'name': 'privacy_statement', 'type': 'text'}, {'name': 'public_burden_statement', 'type': 'text'}]}",
      "sidebar": "{'content': 'The left sidebar contains a login form for returning users and links for password recovery and social login. Its purpose is to facilitate user authentication and access to the platform.', 'purpose': 'User Authentication'}",
      "sidebar_has_menu": false,
      "migration_group": "Blog Post"
      }
    """
    system_instructions = "You are a skilled SEO and content structure analyst with expertise in site architecture, content classification, and CMS migrations. Your goal is to help organize URLs into clear content types to support site migration efforts."
    response = call_ai(
        prompt,
        system_instructions,
        new_json
    )
    # Write the response to a new JSON file
    migration_groups_json = 'data/crawl-analysis/migration_groups.json'

    with open(migration_groups_json, 'w', encoding='utf-8') as f:
        f.write(response)
    print(f"Migration groups assigned and saved to {migration_groups_json}")

    if not response:
      print("No migration groups found. Skipping sidebar analysis.")
      exit(0)

    # Check if the sidebar column has any content
    # new_json_df = polars.read_json(new_json)
    # has_sidebar = new_json_df.select('sidebar').any()
    
    # if 'sidebar' not in new_json_df.columns:
    #   print("No sidebar column found in the migration groups JSON. Skipping sidebar analysis.")
    #   exit(0)

    # if not has_sidebar:
    #   print("No sidebar content found in the migration groups JSON. Skipping sidebar analysis.")
    #   exit(0)
    
    # Pass #2: If the sidebar column has content, analyze the content, rewrite the sidebar content so similar sidebars have the same description.
    pass2_prompt = """
      You are given a JSON file that contains site crawl data. The JSON includes a key titled "sidebar" that provides information about the sidebar content for each page.
      Your task is to analyze the sidebar content and rewrite and consolidate the data to make similar sidebars use the same description.
      Return the original JSON data, with an additional key called "streamlined_sidebar" containing the new description.
      Important guidelines:
      - Use the information in the migration_group key to help identify sidebars that are similar and may belong in the same group.
      - Focus on the purpose and content of the sidebar.
      - Use consistent language and terminology.
      - If you encounter a sidebar with no content, you may leave it unchanged.
    """

    sidebar_response = call_ai(
        pass2_prompt,
        system_instructions,
        migration_groups_json
    )

    # Write the response to a new JSON file
    sidebar_json = 'data/crawl-analysis/sidebar.json'

    with open(sidebar_json, 'w', encoding='utf-8') as f:
        f.write(sidebar_response)
    print(f"Sidebar content rewritten and saved to {sidebar_json}")
