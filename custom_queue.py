from queue import Queue
from typing import Any, Optional
from enum import Enum
import uuid
import time
from threading import Lock

class QueueMode(Enum):
    PURE_FIFO = 1      # Pure FIFO mode
    TWO_LEVEL = 2      # Two-level priority queue
    STRICT_PRIORITY = 3 # Strict priority queue

class PriorityItem:
    def __init__(self, item: Any, priority: int = 0, sequence: int = 0):
        self.item = item
        self.priority = priority
        self.sequence = sequence  # For maintaining FIFO order
    
    def __lt__(self, other):
        return self.priority > other.priority or \
               (self.priority == other.priority and self.sequence < other.sequence)

class CustomQueue:
    def __init__(self):
        self.queue = Queue()
        self.sequence_counter = 0
        self.lock = Lock()  # Add lock
    
    def put(self, item: Any, priority: int = 0) -> None:
        """Put an item into the queue with specified priority"""
        with self.lock:
            priority_item = PriorityItem(item, priority, self.sequence_counter)
            self.sequence_counter += 1
            self.queue.put(priority_item)
    
    def get(self, mode: QueueMode = QueueMode.PURE_FIFO) -> Optional[Any]:
        """Get an item from the queue based on the specified mode"""
        with self.lock:
            if self.queue.empty():
                return None
                
            # Convert queue to list for sorting
            items = []
            while not self.queue.empty():
                items.append(self.queue.get())
                
            if mode == QueueMode.PURE_FIFO:
                items.sort(key=lambda x: x.sequence)
            elif mode == QueueMode.TWO_LEVEL:
                items.sort(key=lambda x: (-1 if x.priority > 0 else 0, x.sequence))
            else:  # STRICT_PRIORITY
                items.sort()
                
            # Get first item and put back the rest
            result = items[0].item
            for item in items[1:]:
                self.queue.put(item)
                
            return result
    
    def empty(self) -> bool:
        """Check if the queue is empty"""
        return self.queue.empty()
    
    def remove_task(self, task_id: str) -> None:
        """Remove a task from queue by its task_id"""
        with self.lock:
            items = []
            while not self.queue.empty():
                item = self.queue.get()
                if item.item.task_id != task_id:
                    items.append(item)
                    
            # Put back the remaining items
            for item in items:
                self.queue.put(item)

class Task:
    def __init__(self, 
                 request_body: dict,
                 requester_id: int,
                 is_urgent: bool = False,
                 retry_count: int = 0,
                 first_provider_id: int = None,
                 task_id: str = None):
        """
        Args:
            request_body: The POST request body containing task details
            requester_id: ID of the user requesting the task
            is_urgent: Whether this is an urgent request due to computing power shortage
            retry_count: Number of times this task has been retried
            first_provider_id: ID of the first provider who processed this task
            task_id: Unique identifier for the task
        """
        self.request_body = request_body
        self.requester_id = requester_id
        self.is_urgent = is_urgent
        self.retry_count = retry_count
        self.first_provider_id = first_provider_id
        self.task_id = task_id or str(uuid.uuid4())
        self.created_at = int(time.time())  # Add creation timestamp