import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone

from langchain_pinecone import PineconeVectorStore



if __name__ == "__main__":
    print("ingesting data...")
    os.environ['PINECONE_API_KEY'] = ''
    # load pdf document
    pc = Pinecone(api_key="")

    loader = PyPDFLoader("1.pdf")
    document = loader.load()
    
    # split entire documents into chunks  
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(document)
    print(f"created {len(texts)} chunks")

    # create vector embeddings and save it in pinecone database
    index = pc.Index("sichat")
    print(index)
    embeddings = OpenAIEmbeddings(openai_api_key="")
    PineconeVectorStore.from_documents(texts, embeddings, index_name="")