import asyncio
import uuid
from fastapi import HTTPException
from typing import Dict, Tuple

from database import is_token_valid

class TaskHandler:
    def __init__(self):
        self.task_queue = asyncio.PriorityQueue()
        self.tasks: Dict[str, Dict] = {}
        self.task_events: Dict[str, asyncio.Event] = {}

    async def process_chat_completion(self, path: str, request: dict) -> dict:
        """Process chat completion request"""
        task_id = str(uuid.uuid4())
        try:
            # Extract token from path
            parts = path.split('/')
            token = parts[0] if parts else ""
            
            # Set priority based on token validity
            priority = 1 if is_token_valid(token) else 10
            
            self.tasks[task_id] = request
            self.task_events[task_id] = asyncio.Event()
            
            await self.task_queue.put((priority, task_id))
            
            try:
                await asyncio.wait_for(self.task_events[task_id].wait(), timeout=30)
            except asyncio.TimeoutError:
                self._cleanup_task(task_id)
                raise HTTPException(status_code=408, detail="Request timeout")
                
            result = self.tasks.pop(task_id)['result']
            self.task_events.pop(task_id)
            return result
        except Exception as e:
            self._cleanup_task(task_id)
            raise HTTPException(status_code=500, detail=str(e))

    async def get_next_task(self, token: str) -> Tuple[str, dict]:
        """Get next task from queue"""
        try:
            if not is_token_valid(token):
                raise HTTPException(status_code=403, detail="Invalid token")
                
            _, task_id = await self.task_queue.get()
            request_body = self.tasks[task_id]
            return task_id, request_body
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=404, detail="No tasks available")

    def submit_task_result(self, token: str, task_id: str, result: dict) -> dict:
        """Submit result for a task"""
        if not is_token_valid(token):
            raise HTTPException(status_code=403, detail="Invalid token")
            
        if task_id in self.tasks:
            self.tasks[task_id]['result'] = result
            self.task_events[task_id].set()
            return {"status": "success"}
        else:
            raise HTTPException(status_code=404, detail="Task ID not found")

    def _cleanup_task(self, task_id: str):
        """Clean up task data"""
        self.tasks.pop(task_id, None)
        self.task_events.pop(task_id, None) 