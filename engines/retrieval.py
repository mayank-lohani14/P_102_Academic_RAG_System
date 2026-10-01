# Author: Mayank Lohani
# Email: mayank.24b0101760@gmail.com

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
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
        
    # 1. Get standard FAISS vector retriever
    faiss_retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
    
    try:
        # 2. Extract all stored documents from the FAISS docstore for BM25 keyword search
        all_docs = list(vector_store.docstore._dict.values())
        
        # If a file filter is active, filter the documents for BM25 as well
        if file_filter and file_filter != "all":
            all_docs = [doc for doc in all_docs if doc.metadata.get("source") == file_filter]
            
        if all_docs:
            # 3. Create BM25 Keyword Retriever
            bm25_retriever = BM25Retriever.from_documents(all_docs)
            bm25_retriever.k = 3
            
            # 4. Combine both into a Hybrid Ensemble Retriever (40% Keyword, 60% Vector)
            ensemble_retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, faiss_retriever],
                weights=[0.4, 0.6]
            )
            return ensemble_retriever
    except Exception as e:
        print(f"Hybrid fallback to vector-only due to: {e}")
        
    # Fallback to standard FAISS retriever if extraction fails
    return faiss_retriever