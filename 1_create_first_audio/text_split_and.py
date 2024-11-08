import re
import pandas as pd

def load_replacements(file_path):
    """Load text replacements from an Excel file."""
    df = pd.read_excel(file_path)
    replacements = {}
    for index, row in df.iterrows():
        replacements[row['original']] = row['replace']
    return replacements

def split_text_into_chunks(text, replacements=None, max_chunk_length=120, max_sentence_length=150):
    """Split text into chunks using commas, periods, and other punctuation marks. 
       Sentences exceeding max_sentence_length are split while keeping words intact.
       Remove periods from text after splitting."""
    
    # Load replacements if provided
    if replacements is None:
        replacements = {}

    # Apply replacements
    for original, replace in replacements.items():
        text = text.replace(original, replace)

    # Normalize text, remove redundant whitespace and convert non-ascii quotes to ascii
    text = re.sub(r'\n\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[“”]', '"', text)

    # Define the punctuation marks for splitting
    punctuation_delimiters = r'(?<=[,.!?])'

    # Split the text based on punctuation
    chunks = re.split(punctuation_delimiters, text)

    final_chunks = []
    current_chunk = ""

    for chunk in chunks:
        # Remove periods from the chunk
        chunk = chunk.replace('.', '')
        chunk = chunk.replace('"', '')
        chunk = chunk.replace('(', '')
        chunk = chunk.replace(')', '')
        chunk = chunk.replace('-', ' ')

        # If the current chunk length exceeds the max_sentence_length, split it further
        if len(chunk) > max_sentence_length:
            words = chunk.split()  # Split the chunk into words
            sub_chunk = ""
            for word in words:
                # If adding this word exceeds the max_sentence_length, commit the current sub_chunk
                if len(sub_chunk) + len(word) + 1 > max_sentence_length:
                    final_chunks.append(sub_chunk.strip())
                    sub_chunk = word
                else:
                    sub_chunk += " " + word
            if sub_chunk:
                final_chunks.append(sub_chunk.strip())
        else:
            if len(current_chunk) + len(chunk) <= max_chunk_length:
                current_chunk += chunk
            else:
                final_chunks.append(current_chunk.strip())
                current_chunk = chunk

    # Add the last chunk if it exists
    if current_chunk:
        final_chunks.append(current_chunk.strip())

    # Clean up, remove empty chunks
    final_chunks = [chunk for chunk in final_chunks if chunk]

    # Optionally print each chunk
    for chunk in final_chunks:
        print(f"Chunk: {chunk}\nLength: {len(chunk)}\n")
        if len(chunk) > max_chunk_length:
            print("ERROR: Chunk exceeds maximum length!\n")

    return final_chunks

# Example usage
file_path = 'replaces_words.xlsx'
replacements = load_replacements(file_path)

# Replace text in chunks
text = "Your input text here. This is an example text to split. How does it handle, longer sentences, you may ask? Let's find out!"
result_chunks = split_text_into_chunks(text, replacements=replacements)
