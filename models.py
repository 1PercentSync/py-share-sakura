from pydantic import BaseModel

class SubmitResultRequest(BaseModel):
    task_id: str
    result: dict

# Define acceptable models
ACCEPTABLE_MODELS = [
    {
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
] 