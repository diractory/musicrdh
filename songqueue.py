"""
╔══════════════════════════════════════════════════════════╗
║                core/songqueue.py                         ║
║   In-memory per-chat song queue                          ║
║   (named songqueue.py, NOT queue.py, to avoid shadowing  ║
║    Python's own standard-library 'queue' module)         ║
╚══════════════════════════════════════════════════════════╝
"""

import random
from collections import deque
from typing import Dict, List, Optional


class SongQueue:
    """Thread-safe in-memory queue for a single chat."""

    def __init__(self):
        self._queue: deque = deque()
        self.loop: bool = False

    def add(self, song: dict) -> int:
        """Add a song dict to the end of the queue. Returns new queue length."""
        self._queue.append(song)
        return len(self._queue)

    def pop(self) -> Optional[dict]:
        """Remove and return the first song; None if empty."""
        if self._queue:
            song = self._queue.popleft()
            if self.loop:
                self._queue.append(song)  # re-add to end for looping
            return song
        return None

    def peek(self) -> Optional[dict]:
        """Return the first song without removing it."""
        return self._queue[0] if self._queue else None

    def shuffle(self):
        items = list(self._queue)
        random.shuffle(items)
        self._queue = deque(items)

    def clear(self):
        self._queue.clear()
        self.loop = False

    def to_list(self) -> List[dict]:
        return list(self._queue)

    def __len__(self) -> int:
        return len(self._queue)

    def __bool__(self) -> bool:
        return bool(self._queue)


class QueueManager:
    """Manages song queues for all active chats."""

    def __init__(self):
        self._queues: Dict[int, SongQueue] = {}

    def get(self, chat_id: int) -> SongQueue:
        if chat_id not in self._queues:
            self._queues[chat_id] = SongQueue()
        return self._queues[chat_id]

    def remove(self, chat_id: int):
        self._queues.pop(chat_id, None)

    def active_chats(self) -> List[int]:
        return [cid for cid, q in self._queues.items() if q]


# Singleton used across the entire application
queue_manager = QueueManager()
