# P_102: Academic Question Answering System (RAG)

A local, privacy-first Retrieval-Augmented Generation (RAG) pipeline designed for academic study assistance at ABES Engineering College. This system ingests course PDFs and provides highly accurate, source-grounded answers using local LLMs.

## System Architecture & Features
* **Frontend:** Custom HTML/CSS/JS interface served via FastAPI with streaming real-time text generation.
* **Vector Search:** FAISS index utilizing HuggingFace `all-MiniLM-L6-v2` embeddings for semantic retrieval.
* **Generative AI:** Local LLaMA 3 (via Ollama) restricted by a strict grounding validator to prevent hallucination.
* **Database Logging:** PostgreSQL database via SQLAlchemy for persistent chat interaction tracking.
* **Multi-Layer Validation:** Blocks irrelevant gibberish and ensures responses strictly rely on uploaded course materials.
* **Citation Tracking:** Surfaces exact source file names and page numbers for every generated response.

## Local Setup Instructions
Ensure Python 3.11+, PostgreSQL, and Ollama (with the LLaMA 3 model pulled) are installed on your machine.

1. Create a local PostgreSQL database named `p102_rag` and update credentials in `services/db.py`.
2. Install the required environment dependencies: `pip install -r requirements.txt`
3. Start the application server: `uvicorn main:app --reload`
4. Access the web interface at `http://127.0.0.1:8000`.

## Docker Deployment
To run the fully containerized production version (including the database and web server):
`docker compose up --build`

## Automated Testing Suite
The repository includes a virtual testing suite built to verify the system against the minimum required scenarios (absent answers, multi-page synthesis, direct answers, and irrelevant queries). With the server running, execute the tests in a separate terminal using `python test_suite.py`.

---
**Author:** Mayank Lohani  
