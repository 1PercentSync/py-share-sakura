import asyncio
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# In-memory queue to store task IDs
task_queue = asyncio.Queue()

# Dictionary to store task details {task_id: request_data}
tasks: Dict[str, Dict] = {}

# Dictionary to store asyncio events for each task {task_id: Event}
task_events: Dict[str, asyncio.Event] = {}

# 模型定义算力提供者提交结果的结构
class SubmitResultRequest(BaseModel):
    task_id: str
    result: dict

@app.post("/v1/chat/completions")
async def chat_completions(request: dict):
    """
    接收用户的聊天完成请求，生成任务ID，将任务加入队列，并等待结果返回。
    """
    task_id = str(uuid.uuid4())
    tasks[task_id] = request
    task_events[task_id] = asyncio.Event()
    await task_queue.put(task_id)
    await task_events[task_id].wait()
    result = tasks.pop(task_id)['result']
    task_events.pop(task_id)
    return result

@app.get("/fetch_task")
async def fetch_task():
    """
    供算力提供者调用，获取下一个待处理的任务。
    返回任务ID和请求体。
    """
    try:
        task_id = await task_queue.get()
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