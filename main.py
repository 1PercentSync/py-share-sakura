from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import SubmitResultRequest, ACCEPTABLE_MODELS, FetchTaskRequest
from database import init_db
from handlers import TaskHandler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    init_db()
    yield
    # Shutdown
    # Add cleanup code here if needed

app = FastAPI(lifespan=lifespan)

# Configurere CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize task handler
task_handler = TaskHandler()

@app.post("/{path:path}/v1/chat/completions")
async def chat_completions(path: str, request: dict):
    """Handle chat completion requests"""
    return await task_handler.process_chat_completion(path, request)

@app.post("/{token}/fetch_task")
async def fetch_task(token: str, request: FetchTaskRequest):
    """Fetch next task for processing"""
    # Validate model info against ACCEPTABLE_MODELS
    model_info = request.model_info.dict()
    acceptable_model = next((m for m in ACCEPTABLE_MODELS if m["id"] == model_info["id"]), None)
    
    if not acceptable_model:
        raise HTTPException(status_code=400, detail="Model not supported")
        
    # Validate meta parameters
    if model_info["meta"] != acceptable_model["meta"]:
        raise HTTPException(status_code=400, detail="Model parameters mismatch")
    
    task_id, request_body = await task_handler.get_next_task(token)
    return {"task_id": task_id, "request_body": request_body}

@app.post("/{token}/submit_result")
async def submit_result(token: str, submit: SubmitResultRequest):
    """Submit processing result"""
    return task_handler.submit_task_result(token, submit.task_id, submit.result)

@app.get("/v1/models")
async def list_models():
    """List available models"""
    return {
        "object": "list",
        "data": ACCEPTABLE_MODELS
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 