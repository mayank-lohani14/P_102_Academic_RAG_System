# Author: Mayank Lohani
# Email: mayank.24b0101760@gmail.com

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def parse_stream(response):
    """Helper function to read the streaming NDJSON response from FastAPI."""
    full_text = ""
    sources = []
    error = None
    
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode('utf-8'))
            if data["type"] == "chunk":
                full_text += data["content"]
            elif data["type"] == "sources":
                sources = data["content"]
            elif data["type"] == "error":
                error = data["content"]
                
    return full_text, sources, error

def run_minimum_test_set():
    print("🚀 Starting P_102 RAG Minimum Test Set...\n")
    print("-" * 50)

    # 1. Irrelevant Question Test (Testing Query Validation)
    print("TEST 1: Irrelevant Question")
    print("Sending gibberish query: 'a'")
    res1 = requests.get(f"{BASE_URL}/query?q=a")
    _, _, err1 = parse_stream(res1)
    
    if err1 and "Validation Failed" in err1:
        print("✅ PASS: System instantly blocked the irrelevant query.")
    else:
        print("❌ FAIL: System attempted to process gibberish.")
    print("-" * 50)

    # 2. Absent Answer Test (Testing Prompt Grounding)
    print("TEST 2: Absent Answer")
    print("Sending out-of-context query: 'What is the recipe for chocolate cake?'")
    res2 = requests.get(f"{BASE_URL}/query?q=What is the recipe for chocolate cake?")
    text2, _, err2 = parse_stream(res2)
    
    if "Information not found" in text2 or (err2 and "Validation Warning" in err2):
        print("✅ PASS: System correctly refused to hallucinate outside knowledge.")
    else:
        print("❌ FAIL: System hallucinated an answer not in the PDFs.")
    print("-" * 50)

    # 3 & 4. Direct Answer & Multi-page Test
    print("TEST 3 & 4: Direct PDF Answer & Multi-page")
    print("Sending academic query: 'Summarize the main topics in the uploaded documents'")
    
    start_time = time.time()
    res3 = requests.get(f"{BASE_URL}/query?q=Summarize the main topics in the uploaded documents")
    text3, sources3, _ = parse_stream(res3)
    
    if len(text3) > 10 and len(sources3) > 0:
        print(f"✅ PASS: System generated a {len(text3)}-character response based on uploaded facts.")
        print(f"✅ PASS: System successfully retrieved {len(sources3)} source chunks.")
        
        # Check if multiple unique pages were cited
        unique_pages = set(s['page'] for s in sources3)
        if len(unique_pages) > 1:
            print(f"✅ PASS (Multi-page): System pulled context from multiple distinct pages: {unique_pages}")
        else:
            print("⚠️ NOTE (Multi-page): System pulled from a single page. Try a broader question to trigger multi-page retrieval.")
    else:
        print("❌ FAIL: No answer generated or no sources retrieved. (Ensure you have uploaded a PDF first!)")
    
    print(f"\nResponse Time: {round(time.time() - start_time, 2)} seconds")
    print("-" * 50)
    print("🏁 Testing Complete.")

if __name__ == "__main__":
    try:
        # Quick check to see if the server is running before testing
        requests.get(BASE_URL)
        run_minimum_test_set()
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: FastAPI server is not running. Start it with 'uvicorn main:app --reload' first.")