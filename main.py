# Author: Mayank Lohani
# Email: mayank.24b0101760@gmail.com

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import shutil
import os
from services.ingestion import ingest_pdfs
from domain.qa import answer_query

app = FastAPI(title="Academic Q&A System (P_102)")

os.makedirs("data/study_pdfs", exist_ok=True)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"data/study_pdfs/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    success = ingest_pdfs()
    if success:
        return {"message": f"Successfully indexed {file.filename}"}
    return {"error": "Failed to index document."}

@app.get("/query")
async def query_system(q: str):
    return answer_query(q)

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Academic RAG Assistant</title>
        <style>
            :root {
                --primary: #4f46e5;
                --primary-hover: #4338ca;
                --sidebar-bg: #f9fafb;
                --chat-bg: #ffffff;
                --border: #e5e7eb;
                --text-main: #111827;
                --text-muted: #6b7280;
            }
            body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; height: 100vh; color: var(--text-main); }
            
            /* Sidebar Styles */
            .sidebar { width: 320px; background-color: var(--sidebar-bg); border-right: 1px solid var(--border); padding: 24px; display: flex; flex-direction: column; overflow-y: auto; }
            .logo-area { display: flex; align-items: center; gap: 12px; margin-bottom: 32px; font-weight: 600; font-size: 18px; }
            .section-title { font-size: 12px; font-weight: 600; color: var(--text-muted); letter-spacing: 0.05em; margin-bottom: 16px; text-transform: uppercase; }
            
            .upload-box { border: 2px dashed #d1d5db; border-radius: 8px; padding: 24px 16px; text-align: center; margin-bottom: 12px; background: white; cursor: pointer; }
            .upload-box:hover { border-color: var(--primary); }
            .upload-box input[type="file"] { display: none; }
            .upload-label { font-size: 14px; color: var(--text-main); font-weight: 500; cursor: pointer; }
            .upload-subtext { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
            .file-name-display { font-size: 13px; color: var(--primary); margin-bottom: 12px; word-break: break-all; }
            
            .btn-process { width: 100%; background-color: var(--primary); color: white; border: none; padding: 10px; border-radius: 6px; font-weight: 600; cursor: pointer; transition: 0.2s; margin-bottom: 16px; }
            .btn-process:hover { background-color: var(--primary-hover); }
            .btn-process:disabled { background-color: #9ca3af; cursor: not-allowed; }
            
            .uploaded-list { margin-bottom: 32px; display: flex; flex-direction: column; gap: 8px; }
            .uploaded-item { background: #f3f4f6; padding: 10px 12px; border-radius: 6px; font-size: 12px; display: flex; align-items: center; gap: 8px; color: #374151; border: 1px solid var(--border); }
            
            .status-row { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 12px; align-items: center; }
            .status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: #10b981; margin-right: 8px; }
            .status-value { color: var(--text-muted); font-size: 13px; }
            
            .model-card { background: white; border: 1px solid var(--border); border-radius: 6px; padding: 12px; margin-bottom: 12px; display: flex; align-items: center; gap: 12px; }
            .model-icon { background: #f3f4f6; padding: 6px; border-radius: 4px; font-size: 12px; font-weight: bold; color: var(--text-muted); }
            
            /* Main Chat Styles */
            .main-content { flex: 1; display: flex; flex-direction: column; background-color: var(--chat-bg); }
            .chat-header { padding: 24px 48px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
            .chat-header h1 { font-size: 20px; margin: 0; }
            .chat-header p { margin: 4px 0 0 0; color: var(--text-muted); font-size: 14px; }
            
            .chat-history { flex: 1; overflow-y: auto; padding: 24px 48px; display: flex; flex-direction: column; gap: 24px; }
            
            .message-wrapper { display: flex; gap: 16px; max-width: 800px; }
            .avatar { width: 32px; height: 32px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; }
            .user-msg .avatar { background-color: #e5e7eb; }
            .ai-msg .avatar { background-color: #dcfce7; }
            .message-content { flex: 1; font-size: 15px; line-height: 1.6; padding-top: 4px; }
            
            details { margin-top: 16px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; background: #f8fafc; }
            summary { padding: 12px 16px; background: white; font-weight: 600; font-size: 13px; color: var(--primary); cursor: pointer; user-select: none; border-bottom: 1px solid transparent; }
            details[open] summary { border-bottom-color: var(--border); }
            .sources-content { padding: 16px; font-size: 13px; color: #475569; }
            .source-card { background: white; border: 1px solid var(--border); border-radius: 6px; padding: 12px; margin-bottom: 8px; }
            .source-card:last-child { margin-bottom: 0; }
            
            /* Input Area */
            .input-area { padding: 24px 48px; background: white; border-top: 1px solid var(--border); }
            .input-box { display: flex; gap: 12px; max-width: 800px; position: relative; }
            .input-box input { flex: 1; padding: 16px 48px 16px 16px; border: 1px solid var(--border); border-radius: 8px; font-size: 15px; outline: none; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
            .input-box input:focus { border-color: var(--primary); box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1); }
            .send-btn { position: absolute; right: 8px; top: 8px; bottom: 8px; width: 40px; background: var(--primary); color: white; border: none; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.2s; }
            .send-btn:hover { background: var(--primary-hover); }
        </style>
    </head>
    <body>
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="logo-area">
                📚 <div>
                    <div style="font-size: 16px;">Academic RAG</div>
                    <div style="font-size: 12px; color: var(--text-muted); font-weight: normal;">AI Study Assistant</div>
                </div>
            </div>

            <div class="section-title">DOCUMENTS</div>
            <div class="upload-box" onclick="document.getElementById('file-upload').click()">
                <div class="upload-label">Upload PDF</div>
                <div class="upload-subtext">Click to select academic documents</div>
                <input type="file" id="file-upload" accept=".pdf" onchange="updateFileName()">
            </div>
            <div id="file-name-display" class="file-name-display"></div>
            <button class="btn-process" id="process-btn" onclick="uploadAndProcess()">Upload & Process</button>
            
            <!-- New persistent uploaded files list -->
            <div id="uploaded-list" class="uploaded-list"></div>

            <div class="section-title">SYSTEM STATUS</div>
            <div class="status-row"><div><span class="status-dot"></span>Ollama</div><span class="status-value">Online</span></div>
            <div class="status-row"><div><span class="status-dot"></span>FAISS DB</div><span class="status-value">Ready</span></div>
            <div class="status-row" style="margin-bottom: 32px;"><div><span class="status-dot"></span>RAG System</div><span class="status-value">Ready</span></div>

            <div class="section-title">MODELS</div>
            <div class="model-card">
                <div class="model-icon">LLM</div>
                <div>
                    <div style="font-size: 13px; font-weight: 600;">Llama 3</div>
                    <div style="font-size: 11px; color: var(--text-muted);">Local Generation</div>
                </div>
            </div>
            <div class="model-card">
                <div class="model-icon">EMB</div>
                <div>
                    <div style="font-size: 13px; font-weight: 600;">all-MiniLM</div>
                    <div style="font-size: 11px; color: var(--text-muted);">HuggingFace</div>
                </div>
            </div>
        </div>

        <!-- Main Chat Area -->
        <div class="main-content">
            <div class="chat-header">
                <div>
                    <h1>Academic Question Answering</h1>
                    <p>Ask questions from your ABES study documents</p>
                </div>
                <div style="font-size: 13px; color: #10b981; font-weight: 500; display: flex; align-items: center; gap: 6px;">
                    <span class="status-dot"></span> Local AI
                </div>
            </div>

            <div class="chat-history" id="chat-history"></div>

            <div class="input-area">
                <div class="input-box">
                    <input type="text" id="chat-input" placeholder="Ask a question about your academic documents..." onkeypress="if(event.key === 'Enter') askQuestion()">
                    <button class="send-btn" onclick="askQuestion()">➤</button>
                </div>
                <div style="text-align: center; font-size: 11px; color: var(--text-muted); margin-top: 12px;">
                    Answers are generated only from your uploaded documents.
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
                const file = fileInput.files[0];
                
                if (!file) {
                    alert("Please select a PDF first.");
                    return;
                }

                btn.innerText = "Processing...";
                btn.disabled = true;

                const formData = new FormData();
                formData.append("file", file);

                try {
                    const response = await fetch('/upload', { method: 'POST', body: formData });
                    const result = await response.json();
                    
                    // Add to the permanent list
                    uploadedList.innerHTML += `<div class="uploaded-item">📄 ${file.name}</div>`;
                    
                    btn.innerText = "Processed Successfully!";
                    btn.style.backgroundColor = "#10b981";
                    
                    // Reset upload area after 3 seconds
                    setTimeout(() => {
                        btn.innerText = "Upload & Process";
                        btn.style.backgroundColor = "";
                        btn.disabled = false;
                        document.getElementById('file-name-display').innerText = "";
                        fileInput.value = "";
                    }, 3000);
                } catch (error) {
                    btn.innerText = "Upload Failed";
                    btn.style.backgroundColor = "#ef4444";
                    btn.disabled = false;
                }
            }

            function addMessageToUI(role, content, sources = []) {
                const chatHistory = document.getElementById('chat-history');
                const wrapper = document.createElement('div');
                wrapper.className = `message-wrapper ${role === 'user' ? 'user-msg' : 'ai-msg'}`;
                
                let avatarIcon = role === 'user' ? '👤' : '🤖';
                let headerText = role === 'user' ? 'You' : 'Academic RAG';

                let sourceHtml = '';
                if (role === 'ai' && sources.length > 0) {
                    let cardsHtml = sources.map(s => 
                        `<div class="source-card"><strong>${s.file}</strong><br>Page ${s.page}</div>`
                    ).join('');
                    
                    sourceHtml = `
                        <details>
                            <summary>▶ Retrieved Sources</summary>
                            <div class="sources-content">${cardsHtml}</div>
                        </details>
                    `;
                }

                wrapper.innerHTML = `
                    <div class="avatar">${avatarIcon}</div>
                    <div class="message-content">
                        <div style="font-size: 12px; font-weight: 600; color: var(--text-muted); margin-bottom: 4px;">${headerText}</div>
                        <div>${content.replace(/\\n/g, '<br>')}</div>
                        ${sourceHtml}
                    </div>
                `;
                
                chatHistory.appendChild(wrapper);
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }

            async function askQuestion() {
                const inputField = document.getElementById('chat-input');
                const question = inputField.value.trim();
                if (!question) return;

                addMessageToUI('user', question);
                inputField.value = '';

                const chatHistory = document.getElementById('chat-history');
                const loadingId = 'loading-' + Date.now();
                const loadingWrapper = document.createElement('div');
                loadingWrapper.className = 'message-wrapper ai-msg';
                loadingWrapper.id = loadingId;
                loadingWrapper.innerHTML = `
                    <div class="avatar">🤖</div>
                    <div class="message-content">
                        <div style="font-size: 12px; font-weight: 600; color: var(--text-muted); margin-bottom: 4px;">Academic RAG</div>
                        <div style="color: var(--text-muted);">Thinking...</div>
                    </div>
                `;
                chatHistory.appendChild(loadingWrapper);
                chatHistory.scrollTop = chatHistory.scrollHeight;

                try {
                    const response = await fetch(`/query?q=${encodeURIComponent(question)}`);
                    const data = await response.json();
                    
                    document.getElementById(loadingId).remove();
                    addMessageToUI('ai', data.answer, data.sources);
                } catch (error) {
                    document.getElementById(loadingId).remove();
                    addMessageToUI('ai', "Error connecting to the local AI backend.");
                }
            }
        </script>
    </body>
    </html>
    """