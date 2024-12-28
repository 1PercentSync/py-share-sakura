from queue import Queue
from typing import Any, Optional
from enum import Enum

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
    
    def put(self, item: Any, priority: int = 0) -> None:
        """Put an item into the queue with specified priority"""
        priority_item = PriorityItem(item, priority, self.sequence_counter)
        self.sequence_counter += 1
        self.queue.put(priority_item)
    
    def get(self, mode: QueueMode = QueueMode.PURE_FIFO) -> Optional[Any]:
        """Get an item from the queue based on the specified mode"""
        if self.queue.empty():
            return None
            
        # Convert queue to list for sorting
        items = []
        while not self.queue.empty():
            items.append(self.queue.get())
            
        if mode == QueueMode.PURE_FIFO:
            # Sort only by sequence number
            items.sort(key=lambda x: x.sequence)
        elif mode == QueueMode.TWO_LEVEL:
            # Sort by priority > 0 first, then by sequence
            items.sort(key=lambda x: (-1 if x.priority > 0 else 0, x.sequence))
        else:  # STRICT_PRIORITY
            # Sort by priority first, then by sequence
            items.sort()
            
        # Get first item and put back the rest
        result = items[0].item
        for item in items[1:]:
            self.queue.put(item)
            
        return result
    
    def empty(self) -> bool:
        """Check if the queue is empty"""
        return self.queue.empty()

class Task:
    def __init__(self, 
                 request_body: dict,
                 requester_id: int,
                 is_urgent: bool = False,
                 is_retry: bool = False,
                 first_provider_id: int = None):
        """
        Args:
            request_body: The POST request body containing task details
            requester_id: ID of the user requesting the task
            is_urgent: Whether this is an urgent request due to computing power shortage
            is_retry: Whether this is a retry attempt
            first_provider_id: ID of the first provider who processed this task
        """
        self.request_body = request_body
        self.requester_id = requester_id
        self.is_urgent = is_urgent
        self.is_retry = is_retry
        self.first_provider_id = first_provider_id