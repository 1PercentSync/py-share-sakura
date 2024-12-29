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
