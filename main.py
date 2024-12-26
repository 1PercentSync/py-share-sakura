from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import SubmitResultRequest, ACCEPTABLE_MODELS
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

# Configure CORS
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

@app.get("/fetch_task")
async def fetch_task():
    """Fetch next task for processing"""
    task_id, request_body = await task_handler.get_next_task()
    return {"task_id": task_id, "request_body": request_body}

@app.post("/submit_result")
async def submit_result(submit: SubmitResultRequest):
    """Submit processing result"""
    return task_handler.submit_task_result(submit.task_id, submit.result)

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