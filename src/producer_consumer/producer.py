from __future__ import annotations

import time
from threading import Thread
from typing import Generic, Iterable, Optional, TypeVar

from .buffer import BoundedBuffer

T = TypeVar("T")


class Producer(Thread, Generic[T]):
    """Producer thread that feeds items from a source iterable into a buffer."""

    def __init__(
        self,
        buffer: BoundedBuffer[T],
        source: Iterable[T],
        *,
        sentinel: Optional[object] = None,
        delay_seconds: float = 0.0,
    ) -> None:
        super().__init__(daemon=True)
        self._buffer = buffer
        self._source = source
        self._sentinel = sentinel
        self._delay = delay_seconds

    def run(self) -> None:
        for item in self._source:
            self._buffer.put(item)
            if self._delay > 0:
                time.sleep(self._delay)
        if self._sentinel is not None:
            self._buffer.put(self._sentinel)  # type: ignore[arg-type]

