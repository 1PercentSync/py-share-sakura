from database import is_token_valid
from fastapi import HTTPException
from models import is_valid_model, AVAILABLE_MODELS
from utils import parse_user_token

async def chat_completions_handler(user_token: str, model_name: str, request: dict):
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