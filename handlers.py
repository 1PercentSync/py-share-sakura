from database import is_token_valid, get_user_credit
from fastapi import HTTPException, FastAPI
from models import is_valid_model, AVAILABLE_MODELS
from utils import parse_user_token
from custom_queue import Task
import uuid
import asyncio

async def chat_completions_handler(user_token: str, model_name: str, request: dict, app: FastAPI):
    # Parse user token into user_id and token
    try:
        user_id, token = parse_user_token(user_token)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "Invalid user token format", 
                    "type": "invalid_request_error",
                    "param": "user_token",
                    "code": "invalid_token"
                }
            }
        )
    
    # Validate user token
    if not is_token_valid(user_id, token):
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "Invalid token or banned",
                    "type": "authentication_error",
                    "param": "user_token",
                    "code": "invalid_token"
                }
            }
        )
        
    # Validate model name
    if not is_valid_model(model_name):
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "message": "Invalid model name",
                    "type": "invalid_request_error",
                    "param": "model_name",
                    "code": "invalid_model",
                    "model_name": model_name
                }
            }
        )

    # Get user priority
    user_priority = get_user_credit(user_id)
    
    #Construct task
    task_id = str(uuid.uuid4())
    result_future = asyncio.Future()
    app.state.pending_results[task_id] = result_future
    task = Task(request_body=request, requester_id=user_id, is_urgent=user_priority > 0, is_retry=False, first_provider_id=None, task_id=task_id)
    
    #Add task to queue
    app.state.task_queue.put(task, user_priority)
    
    try:
        result = await asyncio.wait_for(result_future, timeout=180)  # 在这里等待，直到有人调用 future.set_result()
        return result
    except asyncio.TimeoutError:
        # 1. 从 pending_results 中移除
        app.state.pending_results.pop(task_id, None)
        
        # 2. 从任务队列中移除
        await app.state.task_queue.remove_task(task_id)
        
        raise HTTPException(
            status_code=408,
            detail={
                "error": {
                    "message": "Request timeout",
                    "type": "timeout_error",
                    "code": "timeout"
                }
            }
        )
    
async def fetch_task_handler(user_token: str, submit: dict, app: FastAPI):
    return {"message": "Hello World"}

async def submit_result_handler(user_token: str, submit: dict):
    return {"message": "Hello World"}

async def list_models_handler(user_token: str, model_name: str):
    # Parse user token into user_id and token
    try:
        user_id, token = parse_user_token(user_token)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "Invalid user token format", 
                    "type": "invalid_request_error",
                    "param": "user_token",
                    "code": "invalid_token"
                }
            }
        )
        
    # Validate user token
    if not is_token_valid(user_id, token):
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "Invalid token or banned",
                    "type": "authentication_error",
                    "param": "user_token",
                    "code": "invalid_token"
                }
            }
        )
        
    if not is_valid_model(model_name):
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "message": "Invalid model name",
                    "type": "invalid_request_error",
                    "param": "model_name",
                    "code": "invalid_model",
                    "model_name": model_name
                }
            }
        )
    
    # Return model information in the required format
    return {
        "object": "list",
        "data": [AVAILABLE_MODELS[model_name]]
    }