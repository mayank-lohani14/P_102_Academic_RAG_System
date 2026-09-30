# Author: Mayank Lohani
# Email: mayank.24b0101760@gmail.com

import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def ingest_pdfs(pdf_dir="data/study_pdfs", index_dir="faiss_index"):
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
        
    documents = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_dir, filename)
            loader = PyMuPDFLoader(file_path)
            loaded_docs = loader.load()
            
            # Clean metadata for accurate filtering
            for doc in loaded_docs:
                doc.metadata["source"] = filename 
                
            documents.extend(loaded_docs)

    if not documents:
        return False

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = text_splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(index_dir)
    
    return True