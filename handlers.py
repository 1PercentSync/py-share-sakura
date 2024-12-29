from database import is_token_valid, get_user_credit, set_temp_ban
from fastapi import HTTPException, FastAPI
from models import is_valid_model, AVAILABLE_MODELS, verify_model_meta
from utils import parse_user_token
from custom_queue import Task, QueueMode
import uuid
import asyncio
import time

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
    task = Task(request_body=request, requester_id=user_id, is_urgent=user_priority > 0, try_count=0, first_provider_id=None, task_id=task_id)
    
    #Add task to queue
    app.state.task_queue.put(task, user_priority)
    
    try:
        # Initial timeout of 60 seconds
        result = await asyncio.wait_for(result_future, timeout=60)
        return result
    except asyncio.TimeoutError:
        # If task is claimed, enter monitoring loop
        if task.first_provider_id is not None:
            remaining_time = 120  # Additional timeout
            check_interval = 5  # Check every 5 seconds
            
            while remaining_time > 0:
                current_time = time.time()
                # Check if current provider has taken too long
                if task.claimed_at and current_time - task.claimed_at > 60 and task.try_count < 2:
                    # Reset task for retry
                    task.first_provider_id = None
                    task.claimed_at = None
                    task.try_count += 1
                    try:
                        # Wait for new provider
                        result = await asyncio.wait_for(result_future, timeout=60)
                        return result
                    except asyncio.TimeoutError:
                        pass
                    break  # Exit loop if retry timeout
        
        # If total 180 seconds timeout, check retry_count
        if task.retry_count > 1:
            # Set temporary ban for 3 minutes (180 seconds)
            set_temp_ban(user_id, int(time.time()) + 180)
        
        # Remove from pending_results
        app.state.pending_results.pop(task_id, None)
        
        # Remove from task_queue
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
        
    # Verify model meta
    if not verify_model_meta(submit):
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "message": "Invalid model meta",
                    "type": "invalid_request_error",
                    "param": "model_meta",
                    "code": "invalid_model"
                }
            }
        )
    
    # Check if last fetch time is within 10 seconds
    if time.time() - app.state.last_fetch_time < 1:
        queue_mode=QueueMode.PURE_FIFO
    elif time.time() - app.state.last_fetch_time < 5:
        queue_mode=QueueMode.TWO_LEVEL
    else:
        queue_mode=QueueMode.STRICT_PRIORITY
    
    # Update last fetch time
    app.state.last_fetch_time = time.time()
    
    # Get task from queue with time check
    while True:
        task = app.state.task_queue.get(queue_mode)
        
        if task is None:
            return {
                "status": "empty",
                "message": "No tasks available in queue"
            }
            
        current_time = time.time()
        time_elapsed = current_time - task.created_at
        
        # Skip tasks that are likely to timeout soon
        if (task.try_count == 0 and time_elapsed > 58) or \
           (task.try_count == 1 and time_elapsed > 118):
            continue
            
        # Found a valid task
        break
    
    # Set task attributes
    task.is_urgent = queue_mode != QueueMode.PURE_FIFO
    task.try_count += 1
    task.first_provider_id = user_id
    task.claimed_at = time.time()
    
    return task

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