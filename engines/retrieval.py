# Author: Mayank Lohani
# Email: mayank.24b0101760@gmail.com

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

def get_retriever(file_filter=None, index_dir="faiss_index"):
    if not os.path.exists(index_dir):
        return None
        
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vector_store = FAISS.load_local(
        index_dir, 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    
    search_kwargs = {"k": 3}
    
    # Apply Metadata Filtering if a specific file is selected
    if file_filter and file_filter != "all":
        search_kwargs["filter"] = {"source": file_filter}
        
    return vector_store.as_retriever(search_kwargs=search_kwargs)