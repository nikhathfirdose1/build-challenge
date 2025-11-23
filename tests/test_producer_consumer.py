from __future__ import annotations

import threading
import time

import pytest

from src.producer_consumer.buffer import BoundedBuffer
from src.producer_consumer.consumer import Consumer
from src.producer_consumer.producer import Producer
from src.producer_consumer.runner import run_demo


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


def test_get_blocks_until_item_available() -> None:
    buffer: BoundedBuffer[int] = BoundedBuffer(capacity=1)
    consumed: list[int] = []
    consumed_event = threading.Event()

    def consume() -> None:
        consumed.append(buffer.get())
        consumed_event.set()

    worker = threading.Thread(target=consume, daemon=True)
    worker.start()
    time.sleep(0.05)
    assert not consumed_event.is_set()

    buffer.put(99)
    assert consumed_event.wait(timeout=1)
    worker.join(timeout=1)
    assert consumed == [99]


def test_notify_wakes_waiting_threads_on_put_and_get() -> None:
    buffer: BoundedBuffer[int] = BoundedBuffer(capacity=1)
    put_finished = threading.Event()
    get_finished = threading.Event()

    def delayed_put() -> None:
        buffer.put(1)
        put_finished.set()

    def delayed_get() -> None:
        assert buffer.get() == 1
        get_finished.set()

    getter = threading.Thread(target=delayed_get, daemon=True)
    getter.start()
    time.sleep(0.05)

    putter = threading.Thread(target=delayed_put, daemon=True)
    putter.start()

    assert put_finished.wait(timeout=1)
    assert get_finished.wait(timeout=1)
    getter.join(timeout=1)
    putter.join(timeout=1)


def test_waiting_producers_resume_after_consumers_free_space() -> None:
    buffer: BoundedBuffer[int] = BoundedBuffer(capacity=2)
    buffer.put(1)
    buffer.put(2)

    completion_order: list[str] = []
    order_lock = threading.Lock()
    done = threading.Event()

    def blocking_put(name: str, value: int) -> None:
        buffer.put(value)
        with order_lock:
            completion_order.append(name)
            if len(completion_order) == 2:
                done.set()

    producer_a = threading.Thread(target=blocking_put, args=("first", 3), daemon=True)
    producer_b = threading.Thread(target=blocking_put, args=("second", 4), daemon=True)
    producer_a.start()
    producer_b.start()

    time.sleep(0.05)
    assert not done.is_set()

    assert buffer.get() == 1
    assert buffer.get() == 2

    assert done.wait(timeout=1)
    producer_a.join(timeout=1)
    producer_b.join(timeout=1)
    assert sorted(completion_order) == ["first", "second"]


def test_multiple_producers_multiple_consumers() -> None:
    buffer: BoundedBuffer[object] = BoundedBuffer(capacity=4)
    sentinel = object()
    destination: list[str] = []

    items_a = [f"A-{idx}" for idx in range(5)]
    items_b = [f"B-{idx}" for idx in range(5)]

    producers = [
        Producer(buffer=buffer, source=items_a, sentinel=None),
        Producer(buffer=buffer, source=items_b, sentinel=None),
    ]
    consumers = [
        Consumer(buffer=buffer, destination=destination, sentinel=sentinel)
        for _ in range(2)
    ]

    for worker in (*consumers, *producers):
        worker.start()

    for producer in producers:
        producer.join(timeout=2)

    for _ in consumers:
        buffer.put(sentinel)

    for consumer in consumers:
        consumer.join(timeout=2)

    assert sorted(destination) == sorted(items_a + items_b)
    assert len(destination) == len(items_a) + len(items_b)


def test_buffer_rejects_non_positive_capacity() -> None:
    with pytest.raises(ValueError):
        BoundedBuffer(0)


def test_run_demo_single_producer_single_consumer() -> None:
    consumed = run_demo(
        item_count=6,
        buffer_capacity=2,
        producer_count=1,
        consumer_count=1,
        delay_seconds=0.0,
    )
    assert len(consumed) == 6
    assert consumed == [f"item-00{i}" for i in range(1, 7)]


def test_run_demo_multiple_producers_multiple_consumers() -> None:
    consumed = run_demo(
        item_count=20,
        buffer_capacity=4,
        producer_count=2,
        consumer_count=3,
        delay_seconds=0.0,
    )
    assert len(consumed) == 20
    assert len(set(consumed)) == 20


def test_run_demo_correct_item_counts_no_deadlock() -> None:
    total_items = 30
    consumed = run_demo(
        item_count=total_items,
        buffer_capacity=5,
        producer_count=3,
        consumer_count=2,
        delay_seconds=0.0,
    )
    assert len(consumed) == total_items
    assert sorted(consumed) == [f"item-{i:03d}" for i in range(1, total_items + 1)]


def test_run_demo_does_not_deadlock_under_load() -> None:
    result_container: list[list[str]] = []

    def run() -> None:
        result_container.append(
            run_demo(
                item_count=60,
                buffer_capacity=6,
                producer_count=4,
                consumer_count=3,
                delay_seconds=0.005,
            )
        )

    runner = threading.Thread(target=run, daemon=True)
    runner.start()
    runner.join(timeout=5)
    assert not runner.is_alive(), "run_demo should finish without deadlock"
    assert len(result_container) == 1
    assert len(result_container[0]) == 60

