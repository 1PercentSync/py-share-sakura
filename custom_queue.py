from collections import deque
from typing import Any, Optional

class PriorityQueue:
    def __init__(self):
        """Initialize queue to store tasks with priorities"""
        self.queue = deque()  # store tuples of (priority, order, item)
        self.counter = 0  # for maintaining FIFO order within same priority
    
    def push(self, item: Any, priority: int = 0) -> None:
        """Add an item to the queue with given priority"""
        if priority < 0:
            raise ValueError("Priority must be non-negative")
        self.queue.append((priority, self.counter, item))
        self.counter += 1
    
    def pop(self, mode: int) -> Optional[Any]:
        """
        Return the next item based on mode rules without removing it
        mode 1: pure FIFO
        mode 2: two-level FIFO (priority > 0 first, then priority = 0)
        mode 3: strict priority order
        """
        if not self.queue:
            return None
            
        if mode == 1:
            # Mode 1: pure FIFO
            return self.queue[0][2]
            
        elif mode == 2:
            # Mode 2: two-level FIFO
            # First check if there are any items with priority > 0
            for priority, _, item in self.queue:
                if priority > 0:
                    return item
            # If no priority items found, return the first item
            return self.queue[0][2]
            
        elif mode == 3:
            # Mode 3: strict priority order
            max_priority = -1
            result_item = None
            earliest_counter = float('inf')
            
            # Find item with highest priority (and earliest entry if tied)
            for priority, counter, item in self.queue:
                if priority > max_priority or \
                   (priority == max_priority and counter < earliest_counter):
                    max_priority = priority
                    earliest_counter = counter
                    result_item = item
            
            return result_item
        else:
            raise ValueError("Mode must be 1, 2, or 3")

    def remove(self, item: Any) -> None:
        """Remove the specified item from queue"""
        for i, (_, _, queued_item) in enumerate(self.queue):
            if queued_item == item:
                del self.queue[i]
                return
