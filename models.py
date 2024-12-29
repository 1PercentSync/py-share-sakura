# Define available models and their validation parameters
AVAILABLE_MODELS = {
    "sakura-14b-qwen2.5-v1.0-iq4xs": {
        "id": "sakura-14b-qwen2.5-v1.0-iq4xs",
        "object": "model",
        "created": 0,
        "owned_by": "llamacpp",
        "meta": {
            "vocab_type": 2,
            "n_vocab": 152064,
            "n_ctx_train": 131072,
            "n_embd": 5120,
            "n_params": 14770033664,
            "size": 8180228096
        }
    }
}

def get_default_model() -> str:
    """Get the first model from AVAILABLE_MODELS as default"""
    return next(iter(AVAILABLE_MODELS))

def is_valid_model(model_name: str) -> bool:
    return model_name in AVAILABLE_MODELS

def verify_model_meta(model_meta: dict) -> bool:
    # Ensure 'data' is a list and has at least one item
    if not model_meta.get("data") or not isinstance(model_meta["data"], list):
        return False
    
    # Get the first model's data
    model_data = model_meta["data"][0]
    
    # Check if the model ID exists in AVAILABLE_MODELS
    model_id = model_data.get("id")
    if model_id not in AVAILABLE_MODELS:
        return False
    
    # Get the model's meta from AVAILABLE_MODELS
    available_meta = AVAILABLE_MODELS[model_id]["meta"]
    
    # Compare each key in the meta, ignoring 'created'
    for key, value in model_data["meta"].items():
        if key != "created" and available_meta.get(key) != value:
            return False
    
    return True
