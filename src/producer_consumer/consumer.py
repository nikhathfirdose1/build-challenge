from __future__ import annotations

from threading import Thread
from typing import Callable, Generic, List, Optional, TypeVar

from .buffer import BoundedBuffer

T = TypeVar("T")


class Consumer(Thread, Generic[T]):
    """Consumer thread that drains items from a buffer into a destination list."""

    def __init__(
        self,
        buffer: BoundedBuffer[T],
        destination: List[T],
        *,
        sentinel: Optional[object] = None,
        on_item: Optional[Callable[[T], None]] = None,
    ) -> None:
        super().__init__(daemon=True)
        self._buffer = buffer
        self._destination = destination
        self._sentinel = sentinel
        self._on_item = on_item

    def run(self) -> None:
        while True:
            item = self._buffer.get()
            if self._sentinel is not None and item is self._sentinel:
                break
            self._destination.append(item)
            if self._on_item:
                self._on_item(item)

