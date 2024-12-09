from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import warnings
from dotenv import load_dotenv
import openai
import pdfplumber

import os
import warnings
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore

warnings.filterwarnings("ignore")

load_dotenv()
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
uploads_path = './uploads'

openai.api_key = ''

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

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    files = request.files.getlist('files')
    for file in files:
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    return jsonify({'message': 'Files uploaded successfully'}), 200

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("userMessage")
    context = "Identify key clauses in uploaded documents."  # Custom context to fit the case

    os.environ['PINECONE_API_KEY'] = ''
    os.environ['OPENAI_API_KEY'] = 'sk--'
    embeddings = OpenAIEmbeddings(openai_api_key="sk--")
    # os.environ['OPENAI_API_KEY'] = 'sk--'
    embeddings = OpenAIEmbeddings(openai_api_key="sk--")
    vectorstore = PineconeVectorStore(
        index_name="sichat", embedding=embeddings
    )

    chat = ChatOpenAI(verbose=True, temperature=0, model_name="gpt-4")

    qa = RetrievalQA.from_chain_type(
        llm=chat, chain_type="stuff", retriever=vectorstore.as_retriever()
    )

    response = qa.invoke(user_message + "Break it down into sentences that customers can easily understand.")
    print(response ) 
    query_result = response.get("result")
    
    # Print and return the result
    print(f"Query: {response['query']}\nResult:\n{query_result}")
    return jsonify({"botMessage": query_result})

    # return jsonify({"botMessage": res})

if __name__ == '__main__':
    app.run(debug=True)
