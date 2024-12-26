import asyncio
import aiohttp
import json
from typing import Dict

class LLMClient:
    def __init__(self, server_url: str, llama_url: str, token: str, model_info: Dict):
        self.server_url = server_url.rstrip('/')
        self.llama_url = llama_url.rstrip('/')
        self.token = token
        self.model_info = model_info
        self.session = None
    
    async def start(self):
        """Initialize aiohttp session"""
        self.session = aiohttp.ClientSession()
    
    async def stop(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def forward_request(self, task_id: str, request_body: Dict):
        """Forward request to local llama.cpp server"""
        try:
            # Forward the request to llama.cpp server
            async with self.session.post(
                f"{self.llama_url}/v1/chat/completions",
                json=request_body
            ) as response:
                if response.status != 200:
                    raise Exception(f"Llama server returned status {response.status}")
                result = await response.json()
                
                # Submit result back to main server
                async with self.session.post(
                    f"{self.server_url}/{self.token}/submit_result",
                    json={"task_id": task_id, "result": result}
                ) as submit_response:
                    if submit_response.status != 200:
                        raise Exception(f"Failed to submit result, status: {submit_response.status}")
                    
                return True
        except Exception as e:
            print(f"Error processing task {task_id}: {str(e)}")
            return False
    
    async def fetch_and_process(self):
        """Fetch task from server and process it"""
        try:
            async with self.session.post(
                f"{self.server_url}/{self.token}/fetch_task",
                json={"model_info": self.model_info}
            ) as response:
                if response.status == 404:
                    # No tasks available
                    return False
                elif response.status != 200:
                    raise Exception(f"Failed to fetch task, status: {response.status}")
                
                task_data = await response.json()
                task_id = task_data["task_id"]
                request_body = task_data["request_body"]
                
                await self.forward_request(task_id, request_body)
                return True
        except Exception as e:
            print(f"Error fetching task: {str(e)}")
            return False

async def main():
    # Initialize client
    client = LLMClient(
        server_url="http://localhost:8000",
        llama_url="http://localhost:8080",
        token="token",
        model_info={"id": "sakura-14b-qwen2.5-v1.0-iq4xs"}
    )
    
    await client.start()
    
    try:
        print("Client started. Waiting for tasks...")
        while True:
            try:
                # Fetch and process task
                success = await client.fetch_and_process()
                if not success:
                    # If no task available, wait before trying again
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"Error in main loop: {str(e)}")
                await asyncio.sleep(1)
    finally:
        await client.stop()

if __name__ == "__main__":
    asyncio.run(main()) 