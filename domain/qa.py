# Author: Mayank Lohani
# Email: mayank.24b0101760@gmail.com

import json
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from engines.retrieval import get_retriever
from services.db import SessionLocal, ChatLog

# --- 2. Citation/Grounding Validator Phase ---
def check_grounding(context: str, generated_answer: str, model_name: str = "llama3") -> bool:
    """Verifies if the generated answer relies solely on the provided context."""
    if "Information not found" in generated_answer:
        return True
        
    # Added base_url for Docker networking
    validator_llm = Ollama(model=model_name, base_url="http://host.docker.internal:11434")
    validation_prompt = f"""
    Context: {context}
    
    Answer: {generated_answer}
    
    Task: Does the Answer rely strictly and completely on the facts provided in the Context? 
    Reply with ONLY the word "YES" or "NO".
    """
    
    result = validator_llm.invoke(validation_prompt).strip().upper()
    return "YES" in result

def stream_query(user_query: str, file_filter: str = "all"):
    # --- DATABASE CACHE CHECK ---
    db = SessionLocal()
    try:
        cached_log = db.query(ChatLog).filter(
            ChatLog.student_query == user_query,
            ChatLog.target_document == file_filter
        ).first()

        if cached_log:
            print("Cache hit! Returning saved response from PostgreSQL.")
            yield json.dumps({"type": "chunk", "content": f"[Cached Answer] {cached_log.ai_response}"}) + "\n"
            yield json.dumps({"type": "sources", "content": []}) + "\n"
            return
    except Exception as e:
        print(f"Cache check error: {e}")
    finally:
        db.close()

    retriever = get_retriever(file_filter=file_filter)
    if not retriever:
        yield json.dumps({"type": "error", "content": "Database empty. Please upload PDFs first."}) + "\n"
        return
    
    docs = retriever.invoke(user_query)
    
    context = "\n\n".join([
        f"Source: {d.metadata.get('source')} (Page {d.metadata.get('page')})\nContent: {d.page_content}" 
        for d in docs
    ])
    
    sources = [{"file": d.metadata.get('source'), "page": d.metadata.get('page')} for d in docs]
    
    llm_model = "llama3"
    # Added base_url for Docker networking
    llm = Ollama(model=llm_model, base_url="http://host.docker.internal:11434")
    
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
    
    full_answer = ""
    for chunk in llm.stream(prompt):
        full_answer += chunk
        yield json.dumps({"type": "chunk", "content": chunk}) + "\n"
        
    is_grounded = check_grounding(context, full_answer, model_name=llm_model)
    
    if not is_grounded:
        warning_msg = "\n\n⚠️ **Validation Warning:** The AI validator detected that this answer may contain outside knowledge not explicitly found in your uploaded documents."
        yield json.dumps({"type": "error", "content": warning_msg}) + "\n"
        full_answer += warning_msg
        
    db = SessionLocal()
    try:
        new_log = ChatLog(
            student_query=user_query, 
            ai_response=full_answer, 
            target_document=file_filter
        )
        db.add(new_log)
        db.commit()
    finally:
        db.close()
        
    yield json.dumps({"type": "sources", "content": sources}) + "\n"