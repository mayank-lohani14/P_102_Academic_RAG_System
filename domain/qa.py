# Author: Mayank Lohani
# Email: mayank.24b0101760@gmail.com

import json
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from engines.retrieval import get_retriever

def stream_query(user_query: str):
    retriever = get_retriever()
    if not retriever:
        yield json.dumps({"type": "error", "content": "Database empty. Please upload PDFs first."}) + "\n"
        return
    
    # Retrieve relevant document chunks
    docs = retriever.invoke(user_query)
    
    context = "\n\n".join([
        f"Source: {d.metadata.get('source')} (Page {d.metadata.get('page')})\nContent: {d.page_content}" 
        for d in docs
    ])
    
    # Extract page references
    sources = [{"file": d.metadata.get('source').replace('\\', '/').split('/')[-1], "page": d.metadata.get('page')} for d in docs]
    
    llm = Ollama(model="llama3")
    
    prompt_template = PromptTemplate.from_template("""
    You are an academic study assistant for Computer Science Engineering students at ABES Engineering College. 
    Use ONLY the following context to answer the question. 
    If the answer is absent from the context, output exactly: "Information not found in the provided course materials."
    Do not guess or use outside knowledge.
    
    Context:
    {context}
    
    Question: {question}
    Answer:
    """)
    
    prompt = prompt_template.format(context=context, question=user_query)
    
    # 1. Stream the generated text chunk-by-chunk FIRST
    for chunk in llm.stream(prompt):
        yield json.dumps({"type": "chunk", "content": chunk}) + "\n"
        
    # 2. Yield the sources at the VERY END so they appear after the text finishes
    yield json.dumps({"type": "sources", "content": sources}) + "\n"