import asyncio
import uuid
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["*"]
)

# 使用 asyncio.PriorityQueue 替换自定义队列
task_queue = asyncio.PriorityQueue()

# SQLite 数据库初始化
def init_db():
    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            contribution INTEGER DEFAULT 0,
            credit INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def is_token_valid(token: str) -> bool:
    """
    检查token是否存在于数据库中
    """
    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()
    c.execute('SELECT token FROM tokens WHERE token = ?', (token,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Dictionary to store task details {task_id: request_data}
tasks: Dict[str, Dict] = {}

# Dictionary to store asyncio events for each task {task_id: Event}
task_events: Dict[str, asyncio.Event] = {}

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

# 模型定义算力提供者提交结果的结构
class SubmitResultRequest(BaseModel):
    task_id: str
    result: dict

@app.post("/{path:path}/v1/chat/completions")
async def chat_completions(path: str, request: dict):
    """
    接收用户的聊天完成请求，支持基于token的优先级
    """
    try:
        # 从路径中提取token
        parts = path.split('/')
        token = parts[0] if parts else ""
        
        # 设置优先级：有效token为1，否则为10
        priority = 1 if is_token_valid(token) else 10
        
        task_id = str(uuid.uuid4())
        tasks[task_id] = request
        task_events[task_id] = asyncio.Event()
        
        await task_queue.put((priority, task_id))
        
        # Add timeout mechanism
        try:
            await asyncio.wait_for(task_events[task_id].wait(), timeout=30)
        except asyncio.TimeoutError:
            # Cleanup if timeout
            tasks.pop(task_id, None)
            task_events.pop(task_id, None)
            raise HTTPException(status_code=408, detail="Request timeout")
            
        result = tasks.pop(task_id)['result']
        task_events.pop(task_id)
        return result
    except Exception as e:
        # Cleanup on error
        if task_id in tasks:
            tasks.pop(task_id)
        if task_id in task_events:
            task_events.pop(task_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fetch_task")
async def fetch_task():
    """
    供算力提供者调用，获取下一待处理的任务。
    返回任务ID和请求体。
    """
    try:
        _, task_id = await task_queue.get()  # 解构优先级和task_id
        request_body = tasks[task_id]
        return {"task_id": task_id, "request_body": request_body}
    except Exception:
        raise HTTPException(status_code=404, detail="No tasks available")

@app.post("/submit_result")
async def submit_result(submit: SubmitResultRequest):
    """
    接收算力提供者提交的处理结果，并触发用户请求的返回。
    """
    task_id = submit.task_id
    if task_id in tasks:
        tasks[task_id]['result'] = submit.result
        task_events[task_id].set()  # 触发事件，通知用户请求可以返回结果
        return {"status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Task ID not found") 

@app.get("/v1/models")
async def list_models():
    """
    Return the list of available models in the required format
    """
    return {
        "object": "list",
        "data": ACCEPTABLE_MODELS
    }

# 添加管理token的接口
@app.post("/admin/token")
async def add_token(token: str, contribution: int = 0, credit: int = 0):
    """添加或更新token及其相关信息"""
    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO tokens (token, contribution, credit) 
        VALUES (?, ?, ?)
    ''', (token, contribution, credit))
    conn.commit()
    conn.close()
    return {"status": "success"}

# 添加查询token信息的接口
@app.get("/admin/token/{token}")
async def get_token_info(token: str):
    """查询token的信息"""
    conn = sqlite3.connect('tokens.db')
    c = conn.cursor()
    c.execute('SELECT token, contribution, credit FROM tokens WHERE token = ?', (token,))
    result = c.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="Token not found")
    
    return {
        "token": result[0],
        "contribution": result[1],
        "credit": result[2]
    }

# 在应用启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    init_db()

# 添加启动代码
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 