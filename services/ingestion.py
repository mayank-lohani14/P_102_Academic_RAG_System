# Author: Mayank Lohani (Roll No: 2400320100677)
# Email: mayank.24b0101760@gmail.com
# Project: P_102 Academic Question Answering System

import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def ingest_pdfs(pdf_dir="data/study_pdfs", index_dir="faiss_index"):
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
        
    documents = []
    # Extract and clean text using PyMuPDF
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_dir, filename)
            loader = PyMuPDFLoader(file_path)
            documents.extend(loader.load())

    if not documents:
        return False

    # Chunk the extracted metadata
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = text_splitter.split_documents(documents)
    
    # Embed and index using FAISS
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(index_dir)
    
    return True