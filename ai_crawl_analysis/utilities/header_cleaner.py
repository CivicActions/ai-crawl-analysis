import re

def clean_header(header):
    """
    Clean a CSV header by removing non-alphanumeric characters (except underscores and spaces),
    converting to lowercase, and replacing spaces with underscores.
    :param header: The header string to clean.
    :return: The cleaned header string.
    """
    if not header:
        return header

    # Remove non-alphanumeric characters except underscores and spaces, then lowercase and replace spaces with underscores
    cleaned = re.sub(r'[^a-zA-Z0-9_ ]', '', header)
    cleaned = cleaned.lower().replace(' ', '_')
    return cleaned
