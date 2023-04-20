import os
import sys
import PyPDF2
import pandas as pd
from openai.embeddings_utils import get_embedding
import openai
import json

openai.api_key_path = 'openai_api_key.txt'

def read_files(input_folder):
    content = []
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.txt'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    content.append((f.read(), file))
            elif file.endswith('.pdf'):
                pdf_obj = open(os.path.join(root, file), 'rb', encoding='utf-8')
                pdf_reader = PyPDF2.PdfFileReader(pdf_obj)
                for page_num in range(pdf_reader.numPages):
                    content.append((pdf_reader.getPage(page_num).extractText(), file))
                pdf_obj.close()
    return content

def split_text(text, chunk_size=2048):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(' '.join(current_chunk) + ' ' + word) < chunk_size:
            current_chunk.append(word)
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(' '.join(current_chunk))


    return chunks

def vectorize_chunks(text_chunks, metadata):
    vectorized_data = []

    for chunk in text_chunks:
        embedding = get_embedding(chunk,"text-embedding-ada-002")
        vectorized_data.append({
            'metadata': metadata,
            'text_chunk': chunk,
            'embedding': embedding
        })

    return vectorized_data

def save_to_json(vectorized_data, output_file):
    with open(output_file, 'w',encoding='utf-8') as f:
        # append the new data to the existing file
        json.dump(vectorized_data, f, ensure_ascii=False)

if __name__ == '__main__':
    input_folder = 'input'
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'vectorized/output.json'
    vectorized_data = []
    text_data = read_files(input_folder)
    for text, file in text_data:
        text_chunks = split_text(text)
        metadata = file
        vectorized_chunks = vectorize_chunks(text_chunks, metadata)
        vectorized_data.extend(vectorized_chunks)
    save_to_json(vectorized_data, output_file)