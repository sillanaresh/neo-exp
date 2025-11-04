from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import shutil
from pathlib import Path

from app.config import settings
from app.vector_store import get_vector_store
from app.document_processor import document_processor
from app.chatbot import chatbot

app = FastAPI(title="Neo RAG Chatbot")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get base directory
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    sources: list
    session_id: str

# Landing page
@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Serve the landing page"""
    return FileResponse(STATIC_DIR / "index.html")

# Health check API
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Neo RAG Chatbot API"}

# Chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint"""
    try:
        result = chatbot.chat(request.message, request.session_id)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Clear conversation
@app.post("/api/clear/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history"""
    chatbot.clear_conversation(session_id)
    return {"status": "ok", "message": f"Conversation {session_id} cleared"}

# Upload document (admin)
@app.post("/api/admin/upload")
async def upload_document(
    file: UploadFile = File(...),
    password: str = Form(...),
    document_name: Optional[str] = Form(None)
):
    """Upload and process a document (admin only)"""
    # Verify password
    if password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin password")

    # Validate file type
    allowed_extensions = ['.md', '.txt', '.pdf']
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed: {allowed_extensions}"
        )

    # Use provided name or filename
    doc_name = document_name or file.filename

    # Save file temporarily
    temp_path = UPLOAD_DIR / file.filename
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process and add to vector store
        chunks = document_processor.process_and_chunk(
            str(temp_path),
            file_ext[1:],  # Remove the dot
            doc_name
        )

        # Add to Pinecone
        vector_store = get_vector_store()
        num_chunks = vector_store.add_documents(chunks, doc_name)

        # Clean up temp file
        os.remove(temp_path)

        return {
            "status": "success",
            "message": f"Document '{doc_name}' uploaded successfully",
            "chunks_created": num_chunks
        }

    except Exception as e:
        # Clean up on error
        if temp_path.exists():
            os.remove(temp_path)
        # Log the full error for debugging
        import traceback
        print(f"ERROR in upload: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

# List documents
@app.get("/api/admin/documents")
async def list_documents(password: str):
    """List all documents in the system"""
    if password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin password")

    try:
        vector_store = get_vector_store()
        stats = vector_store.list_documents()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search endpoint (for testing)
@app.get("/api/search")
async def search_endpoint(query: str, top_k: int = 5):
    """Search the knowledge base"""
    try:
        vector_store = get_vector_store()
        results = vector_store.search(query, top_k)
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve the main chat interface
@app.get("/chat", response_class=HTMLResponse)
async def chat_interface():
    """Serve the chat interface"""
    return FileResponse(STATIC_DIR / "chat.html")

# Serve the admin interface
@app.get("/admin", response_class=HTMLResponse)
async def admin_interface():
    """Serve the admin interface"""
    return FileResponse(STATIC_DIR / "admin.html")

# Serve static files (HTML/CSS/JS) - mount at the end
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
