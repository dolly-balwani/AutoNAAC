import os
import requests
from typing import List
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, UnstructuredExcelLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

# Use Local Embeddings (no API needed)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_pdfs(directory: str) -> List[Document]:
    """Loads all PDFs from a directory."""
    print(f"Scanning {directory} for PDFs...")
    loader = DirectoryLoader(directory, glob="**/*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()
    print(f"Loaded {len(docs)} PDF pages.")
    return docs

def load_excels(directory: str) -> List[Document]:
    """Loads all Excel files from a directory."""
    print(f"Scanning {directory} for Excel files...")
    loader = DirectoryLoader(directory, glob="**/*.xlsx", loader_cls=UnstructuredExcelLoader)
    try:
        docs = loader.load()
        print(f"Loaded {len(docs)} Excel documents.")
        return docs
    except Exception as e:
        print(f"Warning: Excel loading failed. Error: {e}")
        return []

def fetch_university_data_api() -> List[Document]:
    """Fetches sample university data from a public API."""
    url = "http://universities.hipolabs.com/search?country=India"
    print(f"Fetching API data from {url}...")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            docs = []
            for item in data[:20]:
                content = f"University: {item.get('name')}\nState: {item.get('state-province')}\nWebsite: {item.get('web_pages', [''])[0]}"
                docs.append(Document(page_content=content, metadata={"source": "api", "type": "university_record"}))
            print(f"Fetched {len(docs)} records from API.")
            return docs
        else:
            print(f"API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"API Fetch failed: {e}")
        return []

def ingest_data(data_dir: str):
    """Main function to ingest all data and build vector store."""
    
    # 1. Load PDFs
    pdf_docs = load_pdfs(data_dir)
    
    # 2. Load Excel Sheets
    excel_docs = load_excels(data_dir)

    # 3. Fetch API Data
    api_docs = fetch_university_data_api()
    
    all_docs = pdf_docs + excel_docs + api_docs
    
    print(f"\nTotal documents collected: {len(all_docs)}")
    
    # 4. Split Text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(all_docs)
    
    # 5. Index into ChromaDB
    if splits:
        vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=embeddings, 
            persist_directory="./chroma_db"
        )
        print(f"✅ Successfully indexed {len(splits)} chunks into ChromaDB.")
        return vectorstore
    else:
        print("No documents to index.")
        return None

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    ingest_data("data")
