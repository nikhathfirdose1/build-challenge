from __future__ import annotations

import threading
import time

from src.producer_consumer.buffer import BoundedBuffer
from src.producer_consumer.consumer import Consumer
from src.producer_consumer.producer import Producer


def test_all_items_are_consumed() -> None:
    source_items = list(range(10))
    sentinel = object()
    buffer: BoundedBuffer[object] = BoundedBuffer(capacity=3)
    destination: list[int] = []

    producer = Producer(buffer=buffer, source=source_items, sentinel=sentinel)
    consumer = Consumer(buffer=buffer, destination=destination, sentinel=sentinel)

    producer.start()
    consumer.start()
    producer.join(timeout=2)
    consumer.join(timeout=2)

    assert destination == source_items


def test_buffer_blocks_when_full() -> None:
    buffer: BoundedBuffer[int] = BoundedBuffer(capacity=1)
    buffer.put(1)

    put_completed = threading.Event()

    def put_extra() -> None:
        buffer.put(2)
        put_completed.set()

    worker = threading.Thread(target=put_extra, daemon=True)
    worker.start()
    time.sleep(0.05)
    assert not put_completed.is_set()

    assert buffer.get() == 1
    assert put_completed.wait(timeout=1)
    worker.join(timeout=1)

