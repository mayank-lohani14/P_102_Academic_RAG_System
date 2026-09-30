# Author: Mayank Lohani
# Email: mayank.24b0101760@gmail.com

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from engines.retrieval import get_retriever

def answer_query(user_query: str):
    retriever = get_retriever()
    if not retriever:
        return {"answer": "Database empty. Please upload PDFs first.", "sources": []}
    
    # Retrieve relevant document chunks
    docs = retriever.invoke(user_query)
    
    # Citation and Grounding Validator
    context = "\n\n".join([
        f"Source: {d.metadata.get('source')} (Page {d.metadata.get('page')})\nContent: {d.page_content}" 
        for d in docs
    ])
    
    llm = Ollama(model="llama3")
    
    # Grounded prompt enforcing not-found handling
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
    answer = llm.invoke(prompt)
    
    # Extract page references for the frontend
    sources = [{"file": d.metadata.get('source').replace('\\', '/').split('/')[-1], "page": d.metadata.get('page')} for d in docs]
    
    return {"answer": answer, "sources": sources}