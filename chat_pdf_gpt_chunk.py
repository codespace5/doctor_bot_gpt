import os
from flask import Flask, request, jsonify
import pdfplumber
import openai

uploads_path = './uploads'
openai.api_key = "sk--"

def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file using pdfplumber.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            # Extract text from all pages and join them
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def split_text(text, max_length=4000):
    """
    Split text into smaller chunks to fit within the token limit.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    
    for word in words:
        if len(" ".join(current_chunk + [word])) > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
        else:
            current_chunk.append(word)
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

def generate_gpt_response(user_text, model_name="gpt-4", print_output=False):
    try:
        # Creating text completions using the updated `ChatCompletion` class
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": user_text + " Identify critical clauses such as: Termination causes, High-value clauses, Potential exceptions."}],
            max_tokens=1500  # Adjust max_tokens to leave room for the model's response
        )
        text_output = response['choices'][0]['message']['content'] if response['choices'] else "No response generated."
        if print_output:
            print(text_output)
            
        return text_output
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def main():
    filename = '1.pdf'
    file_path = os.path.join(uploads_path, filename)
    
    if os.path.exists(file_path):
        print("File found.")
        text = extract_text_from_pdf(file_path)
        
        # Split the text into chunks to stay within token limits
        text_chunks = split_text(text, max_length=4000)
        results = []
        
        for chunk in text_chunks:
            result = generate_gpt_response(chunk, model_name="gpt-4")
            if result:
                results.append(result)
        
        # Combine results
        final_result = "\n\n".join(results)
        print(final_result)
    else:
        print("File not found.")
        return "Failure"

# Run the main function
if __name__ == "__main__":
    main()
