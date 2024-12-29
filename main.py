from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from handlers import list_models_handler, chat_completions_handler
from models import get_default_model
from custom_queue import CustomQueue  # 导入 CustomQueue 类

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    init_db()
    # Initialize a custom queue
    task_queue = CustomQueue()
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

@app.post("/{user_token}/v1/chat/completions")
async def chat_completions_default(user_token: str, request: dict):
    """Handle chat completion request with default model"""
    return await chat_completions_handler(user_token, get_default_model(), request)

@app.post("/{user_token}/{model_name}/v1/chat/completions")
async def chat_completions(user_token: str, model_name: str, request: dict):
    # Handle chat completion request with user token and model name
    return await chat_completions_handler(user_token, model_name, request)

@app.post("/{user_token}/fetch_task")
async def fetch_task(user_token: str, request: dict):
    return {"message": "Hello World"}

@app.post("/{user_token}/submit_result")
async def submit_result(user_token: str, submit: dict):
    """Submit processing result"""
    return {"message": "Hello World"}

@app.get("/{user_token}/v1/models")
async def list_default_models(user_token: str):
    """Handle request without model_name by using default model"""
    return await list_models_handler(user_token, get_default_model())

@app.get("/{user_token}/{model_name}/v1/models")
async def list_models(user_token: str, model_name: str):
    return await list_models_handler(user_token, model_name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 