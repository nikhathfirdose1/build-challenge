from __future__ import annotations

from collections import deque
from threading import Condition
from typing import Deque, Generic, TypeVar

T = TypeVar("T")


class BoundedBuffer(Generic[T]):
    """Thread-safe bounded FIFO buffer with explicit wait/notify semantics."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity = capacity
        self._buffer: Deque[T] = deque()
        self._condition = Condition()

    def put(self, item: T) -> None:
        """Block until space is available, then store the item."""
        with self._condition:
            while len(self._buffer) >= self._capacity:
                self._condition.wait()
            self._buffer.append(item)
            self._condition.notify_all()

    def get(self) -> T:
        """Block until an item is available, then return it."""
        with self._condition:
            while not self._buffer:
                self._condition.wait()
            item = self._buffer.popleft()
            self._condition.notify_all()
            return item

    def current_size(self) -> int:
        """Return the current number of buffered items."""
        with self._condition:
            return len(self._buffer)

    @property
    def capacity(self) -> int:
        """Maximum number of items the buffer can hold."""
        return self._capacity

