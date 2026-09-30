# Author: Mayank Lohani
# Email: mayank.24b0101760@gmail.com

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
import shutil
import os
import json
import re
from services.ingestion import ingest_pdfs
from domain.qa import stream_query

app = FastAPI(title="Academic Q&A System (P_102)")

os.makedirs("data/study_pdfs", exist_ok=True)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"data/study_pdfs/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    success = ingest_pdfs()
    if success:
        return {"message": "Success", "filename": file.filename}
    return {"error": "Failed to index document."}

@app.get("/query")
async def query_system(q: str, filter: str = "all"):
    # --- 1. Query Validation Phase ---
    cleaned_query = q.strip()
    
    # Check for empty or excessively short queries
    if len(cleaned_query) < 3:
        async def validation_error():
            yield json.dumps({"type": "error", "content": "Validation Failed: Query is too short. Please ask a specific academic question."}) + "\n"
        return StreamingResponse(validation_error(), media_type="application/x-ndjson")
    
    # Check for gibberish (must contain at least one alphanumeric word)
    if not re.search(r'[a-zA-Z0-9]', cleaned_query):
        async def validation_error():
            yield json.dumps({"type": "error", "content": "Validation Failed: Please use valid alphanumeric characters for your question."}) + "\n"
        return StreamingResponse(validation_error(), media_type="application/x-ndjson")

    # If passes validation, route to the retrieval and LLM engine
    return StreamingResponse(stream_query(cleaned_query, file_filter=filter), media_type="application/x-ndjson")

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Academic RAG Assistant - ABES Engineering College</title>
        <style>
            :root {
                --primary: #6366f1;
                --primary-hover: #4f46e5;
                --primary-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                --sidebar-bg: #f8fafc;
                --chat-bg: #ffffff;
                --border: #e2e8f0;
                --text-main: #0f172a;
                --text-muted: #64748b;
                --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
                --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            }
            * { box-sizing: border-box; }
            body { margin: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; height: 100vh; color: var(--text-main); background: #f1f5f9; }
            
            .sidebar { width: 340px; background-color: var(--sidebar-bg); border-right: 1px solid var(--border); padding: 24px; display: flex; flex-direction: column; overflow-y: auto; }
            .logo-area { display: flex; align-items: center; gap: 14px; margin-bottom: 28px; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
            .logo-icon { width: 42px; height: 42px; background: var(--primary-gradient); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; color: white; box-shadow: var(--shadow-sm); }
            .section-title { font-size: 11px; font-weight: 700; color: var(--text-muted); letter-spacing: 0.08em; margin-bottom: 12px; text-transform: uppercase; }
            
            .upload-box { border: 2px dashed #cbd5e1; border-radius: 12px; padding: 20px 16px; text-align: center; margin-bottom: 12px; background: white; cursor: pointer; transition: all 0.2s ease; }
            .upload-box:hover { border-color: var(--primary); background: #f8fafc; box-shadow: var(--shadow-sm); }
            .upload-box input[type="file"] { display: none; }
            .upload-label { font-size: 14px; color: var(--text-main); font-weight: 600; cursor: pointer; }
            .upload-subtext { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
            .file-name-display { font-size: 13px; color: var(--primary); font-weight: 500; margin-bottom: 12px; word-break: break-all; text-align: center; }
            
            .btn-process { width: 100%; background: var(--primary-gradient); color: white; border: none; padding: 12px; border-radius: 10px; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.2s; margin-bottom: 20px; box-shadow: var(--shadow-sm); }
            .btn-process:hover { opacity: 0.95; transform: translateY(-1px); box-shadow: var(--shadow-md); }
            
            .uploaded-list { margin-bottom: 24px; display: flex; flex-direction: column; gap: 8px; }
            .uploaded-item { background: white; padding: 10px 14px; border-radius: 8px; font-size: 12px; display: flex; align-items: center; gap: 10px; color: #334155; border: 1px solid var(--border); box-shadow: var(--shadow-sm); font-weight: 500; }
            
            .status-container { background: white; border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-top: auto; box-shadow: var(--shadow-sm); }
            .status-row { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 10px; align-items: center; font-weight: 500; }
            .status-row:last-child { margin-bottom: 0; }
            .status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: #10b981; margin-right: 8px; box-shadow: 0 0 6px #10b981; }
            .status-value { color: var(--text-muted); font-size: 12px; font-weight: 600; background: #f1f5f9; padding: 2px 8px; border-radius: 6px; }
            
            .main-content { flex: 1; display: flex; flex-direction: column; background-color: var(--chat-bg); }
            .chat-header { padding: 20px 40px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; background: white; box-shadow: var(--shadow-sm); }
            .chat-header h1 { font-size: 18px; margin: 0; font-weight: 700; color: var(--text-main); }
            .chat-header p { margin: 2px 0 0 0; color: var(--text-muted); font-size: 13px; }
            
            .chat-history { flex: 1; overflow-y: auto; padding: 32px 40px; display: flex; flex-direction: column; gap: 24px; scroll-behavior: smooth; }
            
            .message-wrapper { display: flex; gap: 16px; max-width: 850px; animation: fadeIn 0.3s ease; }
            @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
            
            .avatar { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; box-shadow: var(--shadow-sm); }
            .user-msg .avatar { background: #e2e8f0; color: #334155; }
            .ai-msg .avatar { background: #e0e7ff; color: var(--primary); }
            .message-content { flex: 1; font-size: 14px; line-height: 1.7; padding-top: 6px; }
            
            details { margin-top: 14px; border: 1px solid var(--border); border-radius: 10px; overflow: hidden; background: #f8fafc; box-shadow: var(--shadow-sm); }
            summary { padding: 10px 14px; background: white; font-weight: 600; font-size: 12px; color: var(--primary); cursor: pointer; user-select: none; border-bottom: 1px solid var(--border); }
            summary:hover { background: #f8fafc; }
            .sources-content { padding: 14px; font-size: 12px; color: #475569; display: flex; gap: 8px; flex-wrap: wrap; }
            .source-card { background: white; border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px; box-shadow: var(--shadow-sm); flex: 1; min-width: 200px; }
            
            .input-area { padding: 20px 40px; background: white; border-top: 1px solid var(--border); box-shadow: 0 -4px 6px -1px rgb(0 0 0 / 0.02); }
            .input-box { display: flex; gap: 12px; max-width: 850px; position: relative; margin-bottom: 10px; }
            .input-box input { flex: 1; padding: 14px 50px 14px 18px; border: 1px solid var(--border); border-radius: 12px; font-size: 14px; outline: none; background: #f8fafc; transition: all 0.2s; }
            .input-box input:focus { border-color: var(--primary); background: white; box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15); }
            .send-btn { position: absolute; right: 6px; top: 6px; bottom: 6px; width: 42px; background: var(--primary-gradient); color: white; border: none; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: opacity 0.2s; }
            .send-btn:hover { opacity: 0.9; }
            
            .filter-container { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-muted); font-weight: 500; }
            .filter-dropdown { padding: 6px 12px; border-radius: 8px; border: 1px solid var(--border); font-size: 12px; outline: none; background: #f8fafc; cursor: pointer; color: var(--text-main); font-weight: 500; }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="logo-area">
                <div class="logo-icon">📚</div>
                <div>
                    <div style="font-size: 15px; font-weight: 700;">Academic RAG</div>
                    <div style="font-size: 11px; color: var(--text-muted); font-weight: 500;">AI Study Assistant</div>
                </div>
            </div>

            <div class="section-title">Documents Management</div>
            <div class="upload-box" onclick="document.getElementById('file-upload').click()">
                <div class="upload-label">Upload Study PDF</div>
                <div class="upload-subtext">Click to browse course notes</div>
                <input type="file" id="file-upload" accept=".pdf" onchange="updateFileName()">
            </div>
            <div id="file-name-display" class="file-name-display"></div>
            <button class="btn-process" id="process-btn" onclick="uploadAndProcess()">Upload & Process</button>
            
            <div class="section-title">Indexed Files</div>
            <div id="uploaded-list" class="uploaded-list"></div>

            <div class="section-title" style="margin-top: auto;">System Status</div>
            <div class="status-container">
                <div class="status-row"><div><span class="status-dot"></span>Ollama LLM</div><span class="status-value">Online</span></div>
                <div class="status-row"><div><span class="status-dot"></span>PostgreSQL DB</div><span class="status-value">Ready</span></div>
                <div class="status-row"><div><span class="status-dot"></span>FAISS Index</div><span class="status-value">Ready</span></div>
            </div>
        </div>

        <div class="main-content">
            <div class="chat-header">
                <div>
                    <h1>Academic Question Answering</h1>
                    <p>ABES Engineering College • CSE Department</p>
                </div>
                <div style="font-size: 12px; color: #10b981; font-weight: 600; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 6px 12px; border-radius: 20px; display: flex; align-items: center; gap: 6px;">
                    <span class="status-dot" style="margin: 0;"></span> Local AI Active
                </div>
            </div>

            <div class="chat-history" id="chat-history"></div>

            <div class="input-area">
                <div class="input-box">
                    <input type="text" id="chat-input" placeholder="Ask a question about your uploaded academic documents..." onkeypress="if(event.key === 'Enter') askQuestion()">
                    <button class="send-btn" onclick="askQuestion()">➤</button>
                </div>
                <div class="filter-container">
                    <span>🔍 Search Context Scope:</span>
                    <select id="doc-filter" class="filter-dropdown">
                        <option value="all">All Uploaded Documents</option>
                    </select>
                </div>
            </div>
        </div>

        <script>
            function updateFileName() {
                const file = document.getElementById('file-upload').files[0];
                if (file) document.getElementById('file-name-display').innerText = file.name;
            }

            async function uploadAndProcess() {
                const fileInput = document.getElementById('file-upload');
                const btn = document.getElementById('process-btn');
                const uploadedList = document.getElementById('uploaded-list');
                const filterDropdown = document.getElementById('doc-filter');
                const file = fileInput.files[0];
                
                if (!file) return;

                btn.innerText = "Processing vector embeddings...";
                
                const formData = new FormData();
                formData.append("file", file);

                try {
                    const response = await fetch('/upload', { method: 'POST', body: formData });
                    const data = await response.json();
                    
                    uploadedList.innerHTML += `<div class="uploaded-item">📄 ${data.filename}</div>`;
                    
                    const option = document.createElement("option");
                    option.value = data.filename;
                    option.text = data.filename;
                    filterDropdown.appendChild(option);
                    
                    btn.innerText = "Processed Successfully!";
                    btn.style.background = "linear-gradient(135deg, #10b981 0%, #059669 100%)";
                    
                    setTimeout(() => {
                        btn.innerText = "Upload & Process";
                        btn.style.background = "";
                        document.getElementById('file-name-display').innerText = "";
                        fileInput.value = "";
                    }, 3000);
                } catch (error) {
                    btn.innerText = "Upload Failed";
                    btn.style.background = "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)";
                }
            }

            function addUserMessage(content) {
                const chatHistory = document.getElementById('chat-history');
                const wrapper = document.createElement('div');
                wrapper.className = 'message-wrapper user-msg';
                wrapper.innerHTML = `<div class="avatar">👤</div><div class="message-content"><div style="font-size: 11px; font-weight: 700; color: var(--text-muted); margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.05em;">You</div><div style="background: #ffffff; padding: 12px 16px; border-radius: 12px; border: 1px solid var(--border); box-shadow: var(--shadow-sm);">${content}</div></div>`;
                chatHistory.appendChild(wrapper);
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }

            async function askQuestion() {
                const inputField = document.getElementById('chat-input');
                const filterValue = document.getElementById('doc-filter').value;
                const question = inputField.value.trim();
                
                if (!question) return;

                addUserMessage(question);
                inputField.value = '';

                const chatHistory = document.getElementById('chat-history');
                const msgId = 'msg-' + Date.now();
                
                const aiWrapper = document.createElement('div');
                aiWrapper.className = 'message-wrapper ai-msg';
                aiWrapper.innerHTML = `
                    <div class="avatar">🤖</div>
                    <div class="message-content">
                        <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.05em;">Academic RAG Assistant</div>
                        <div style="background: #ffffff; padding: 16px; border-radius: 12px; border: 1px solid var(--border); box-shadow: var(--shadow-sm);">
                            <div id="ans-${msgId}" style="color: var(--text-muted); font-style: italic;">Thinking and searching vector embeddings...</div>
                            <div id="src-${msgId}" style="display: none;"></div>
                        </div>
                    </div>
                `;
                chatHistory.appendChild(aiWrapper);
                chatHistory.scrollTop = chatHistory.scrollHeight;

                try {
                    const response = await fetch(`/query?q=${encodeURIComponent(question)}&filter=${encodeURIComponent(filterValue)}`);
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder("utf-8");
                    
                    const ansDiv = document.getElementById(`ans-${msgId}`);
                    const srcDiv = document.getElementById(`src-${msgId}`);
                    
                    ansDiv.innerHTML = ""; 
                    ansDiv.style.color = "var(--text-main)";
                    ansDiv.style.fontStyle = "normal";
                    
                    let buffer = "";

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        
                        buffer += decoder.decode(value, { stream: true });
                        const lines = buffer.split('\\n');
                        buffer = lines.pop(); 
                        
                        for (const line of lines) {
                            if (!line.trim()) continue;
                            const data = JSON.parse(line);
                            
                            if (data.type === 'sources') {
                                if (data.content.length > 0) {
                                    let cardsHtml = data.content.map(s => 
                                        `<div class="source-card"><strong>📁 ${s.file}</strong><br><span style="color: var(--text-muted);">Page ${s.page}</span></div>`
                                    ).join('');
                                    srcDiv.innerHTML = `<details><summary>📑 Retrieved Sources & Citations</summary><div class="sources-content">${cardsHtml}</div></details>`;
                                    srcDiv.style.display = 'block';
                                }
                            } 
                            else if (data.type === 'chunk') {
                                ansDiv.innerHTML += data.content.replace(/\\n/g, '<br>');
                                chatHistory.scrollTop = chatHistory.scrollHeight;
                            } 
                            else if (data.type === 'error') {
                                ansDiv.innerHTML += `<br><span style="color: #ef4444; font-weight: 600;">${data.content}</span>`;
                                chatHistory.scrollTop = chatHistory.scrollHeight;
                            }
                        }
                    }
                } catch (error) {
                    document.getElementById(`ans-${msgId}`).innerHTML = `<span style="color: #ef4444;">Error connecting to backend container.</span>`;
                }
            }
        </script>
    </body>
    </html>
    """