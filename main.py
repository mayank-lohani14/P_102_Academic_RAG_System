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
        <title>P_102 RAG System</title>
        <style>
            :root {
                --primary: #2563eb;
                --primary-hover: #1d4ed8;
                --bg: #f1f5f9;
                --surface: #ffffff;
                --text: #0f172a;
                --border: #e2e8f0;
            }
            body {
                font-family: system-ui, -apple-system, sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                padding: 40px 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .container {
                background: var(--surface);
                width: 100%;
                max-width: 800px;
                border-radius: 12px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }
            .header {
                background: #0f172a;
                color: white;
                padding: 24px 32px;
                text-align: center;
            }
            .header h2 { margin: 0; font-size: 24px; font-weight: 600; letter-spacing: -0.5px; }
            .header p { margin: 8px 0 0 0; color: #94a3b8; font-size: 14px; }
            .content { padding: 32px; }
            .section-title {
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 16px;
                color: var(--text);
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .upload-box {
                border: 2px dashed #cbd5e1;
                border-radius: 8px;
                padding: 32px 24px;
                text-align: center;
                margin-bottom: 32px;
                background: #f8fafc;
                transition: border-color 0.2s, background 0.2s;
            }
            .upload-box:hover { border-color: var(--primary); background: #f1f5f9; }
            input[type="file"] {
                display: block;
                margin: 0 auto 16px auto;
                font-size: 14px;
                color: #475569;
            }
            input[type="file"]::file-selector-button {
                background: white;
                border: 1px solid var(--border);
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                margin-right: 16px;
                transition: background 0.2s;
            }
            input[type="file"]::file-selector-button:hover { background: #f1f5f9; }
            button, input[type="submit"] {
                background: var(--primary);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: 500;
                cursor: pointer;
                transition: background 0.2s;
                font-size: 14px;
            }
            button:hover, input[type="submit"]:hover { background: var(--primary-hover); }
            .search-box {
                display: flex;
                gap: 12px;
                margin-bottom: 24px;
            }
            input[type="text"] {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid var(--border);
                border-radius: 6px;
                font-size: 15px;
                outline: none;
                transition: border-color 0.2s, box-shadow 0.2s;
            }
            input[type="text"]:focus {
                border-color: var(--primary);
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            }
            .result-box {
                background: white;
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 24px;
                display: none;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            }
            .result-box.active { display: block; }
            .answer-text { line-height: 1.6; margin-bottom: 24px; color: #334155; }
            .sources-list {
                background: #f8fafc;
                padding: 16px;
                border-radius: 6px;
                border: 1px solid #e2e8f0;
                font-size: 13px;
                color: #475569;
            }
            .sources-list strong { color: #1e293b; display: block; margin-bottom: 8px; }
            .sources-list ul { margin: 0; padding-left: 20px; }
            .sources-list li { margin-bottom: 4px; }
            #status { margin-top: 16px; font-size: 14px; font-weight: 500; }
            .footer {
                margin-top: 24px;
                text-align: center;
                color: #64748b;
                font-size: 13px;
                line-height: 1.5;
            }
            .footer strong { color: #475569; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>📚 Academic Question Answering System</h2>
                <p>Retrieval-Augmented Generation (RAG) Document Assistant</p>
            </div>
            
            <div class="content">
                <div class="section-title">📂 1. Upload Study Materials</div>
                <div class="upload-box">
                    <form action="/upload" enctype="multipart/form-data" method="post" target="hiddenFrame">
                        <input name="file" type="file" accept=".pdf" required>
                        <input type="submit" value="Upload & Index Document" onclick="document.getElementById('status').innerText = '⚙️ Processing document with FAISS...'; document.getElementById('status').style.color = '#ca8a04';">
                    </form>
                    <p id="status"></p>
                    <iframe name="hiddenFrame" style="display:none;" onload="if(this.contentWindow.location.href !== 'about:blank'){document.getElementById('status').innerText = '✅ Index Complete! Ready for questions.'; document.getElementById('status').style.color = '#16a34a';}"></iframe>
                </div>

                <div class="section-title">💬 2. Ask a Question</div>
                <div class="search-box">
                    <input type="text" id="q" placeholder="Enter an academic question based on your uploaded PDFs..." onkeypress="if(event.key === 'Enter') ask()">
                    <button onclick="ask()">Ask AI</button>
                </div>
                
                <div id="result-container" class="result-box">
                    <div id="ans" class="answer-text"></div>
                    <div id="sources" class="sources-list" style="display: none;"></div>
                </div>
            </div>
        </div>

        <div class="footer">
            Developed by <strong>Mayank Lohani</strong><br>
            ABES Engineering College • CSE-21
        </div>

        <script>
            async function ask() {
                const resultContainer = document.getElementById('result-container');
                const ansDiv = document.getElementById('ans');
                const sourcesDiv = document.getElementById('sources');
                const q = document.getElementById('q').value;
                
                if (!q.trim()) return;

                resultContainer.classList.add('active');
                ansDiv.innerHTML = '<span style="color: #64748b;">⏳ Retrieving context and generating answer...</span>';
                sourcesDiv.style.display = 'none';
                
                try {
                    const res = await fetch(`/query?q=${encodeURIComponent(q)}`);
                    const data = await res.json();
                    
                    ansDiv.innerHTML = `<strong>Answer:</strong><br><br>${data.answer.replace(/\\n/g, '<br>')}`;
                    
                    let sourcesHtml = '<strong>Retrieved Source Coverage:</strong><ul>';
                    if (data.sources.length === 0) {
                        sourcesHtml += '<li>No matching context found.</li>';
                    } else {
                        data.sources.forEach(s => {
                            sourcesHtml += `<li>${s.file} (Page ${s.page})</li>`;
                        });
                    }
                    sourcesHtml += '</ul>';
                    
                    sourcesDiv.innerHTML = sourcesHtml;
                    sourcesDiv.style.display = 'block';
                } catch (error) {
                    ansDiv.innerHTML = '<span style="color: #dc2626;">❌ An error occurred while fetching the answer.</span>';
                }
            }
        </script>
    </body>
    </html>
    """