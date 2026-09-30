# Author: Mayank Lohani
# Email: mayank.24b0101760@gmail.com

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

def get_retriever(index_dir="faiss_index"):
    if not os.path.exists(index_dir):
        return None
        
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load the FAISS vector database
    vector_store = FAISS.load_local(
        index_dir, 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    
    return vector_store.as_retriever(search_kwargs={"k": 3})