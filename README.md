# AI Migration Tools

## ✨ Description
This repository outlines processes and includes tools used for interpreting data generated from site crawls to inform content migrations. The tools are designed to assist with data migration, data cleaning, and AI-fueled data analysis tasks. The goal is to apply data-based decisions to consolidating the migration of multiple sites.

## 🚀 Features
- Uses `uv` for fast dependency management and isolated execution
- Built with `polars`, `google-genai`, and `python-dotenv`
- Modular script structure runnable via module syntax
- **Crawl Analysis**: Analyze and extract insights from crawled datasets.
- **Deduplication**: Remove duplicate items from columns to ensure data integrity.
- **JSON Expansion**: Expand JSON fields within CSV files into separate columns for easier analysis.
- **Header Cleaning**: Standardize and clean column headers in tabular data.
- **HTML Row Filtering**: Filter out unwanted HTML rows from datasets.
- **AI Integration**: Utilities for making AI calls to enhance or validate data.


## 📁 Directory Structure

- `ai_migrations/`: Core Python modules for data processing.
  - `crawl_analysis.py`: Tools for analyzing crawled data.
  - `deduplicate_column_items.py`: Deduplication utilities.
  - `expand_json_csv.py`: JSON-to-CSV expansion logic.
  - `utilities/`: Helper modules for AI calls, header cleaning, and HTML filtering.
- `data/`: Example input and output datasets.
  - `audit-inputs/`: Raw CSV files for processing.
  - `audit-outputs/`: Processed and expanded CSV files.
- `prompts/`: Prompt templates for AI-powered tasks.
- `temp/`: Temporary scripts and playground files.

## 📦 Requirements

- Python **3.13+**
- [`uv`](https://docs.astral.sh/uv/) (a modern Python package manager)

- Install `uv` (if you don’t already have it)
``` bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # or
    pipx install uv
    # or
    pip install uv
    # or
    brew install uv
```

For mor options, review the [Documentation for installing uv](https://docs.astral.sh/uv/getting-started/installation/)


## 🔧 Getting Started
1. **Clone the repository**:
```bash 
    git clone https://github.com/civicactions/ai-migrations.git
    cd ai-migrations
```

1. **Install dependencies**:
   Install directly from `pyproject.toml`:
   ```bash
   uv pip install -r pyproject.toml
   ```

## Running scripts:
Project scripts are structured as modules. You can 
- Run them using uv run or standard Python module syntax
   ```bash
   uv run -m ai_migrations (WIP)
   ```
**OR**

- Run them using Python directly
  - Activate the virtual environment
  - Then run `python -m ai_migrations`


### Environment variables
The crawl_analysis script requires an API_KEY environment variable. Edit the env.example fiel at the root of the rject to add your AI API Key.

## License

MIT License
