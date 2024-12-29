from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import SubmitResultRequest, ACCEPTABLE_MODELS, FetchTaskRequest
from database import init_db

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

@app.post("/{user_token}/{model_name}/v1/chat/completions")
async def chat_completions(user_token: str, model_name: str, request: dict):
    # Handle chat completion request with user token and model name
    return {"message": "Hello World"}

@app.post("/{user_token}/fetch_task")
async def fetch_task(user_token: str, request: FetchTaskRequest):
    return {"message": "Hello World"}

@app.post("/{user_token}/submit_result")
async def submit_result(user_token: str, submit: SubmitResultRequest):
    """Submit processing result"""
    return {"message": "Hello World"}

@app.get("/{user_token}/{model_name}/v1/models")
async def list_models(user_token: str, model_name: str):
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 