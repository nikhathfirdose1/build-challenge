from __future__ import annotations

import argparse
from typing import List, Sequence

from .buffer import BoundedBuffer
from .consumer import Consumer
from .producer import Producer


def _chunk_items(items: Sequence[str], num_chunks: int) -> List[List[str]]:
    """Distribute items across `num_chunks` buckets (round-robin)."""
    buckets: List[List[str]] = [[] for _ in range(max(1, num_chunks))]
    for index, item in enumerate(items):
        buckets[index % len(buckets)].append(item)
    return [bucket for bucket in buckets if bucket]


def run_demo(
    *,
    item_count: int = 8,
    buffer_capacity: int = 4,
    producer_count: int = 1,
    consumer_count: int = 1,
    delay_seconds: float = 0.01,
) -> List[str]:
    """Execute a sample producer-consumer workflow and return consumed items."""
    items = [f"item-{index:03d}" for index in range(1, item_count + 1)]
    item_groups = _chunk_items(items, producer_count)
    buffer: BoundedBuffer[object] = BoundedBuffer(capacity=buffer_capacity)
    destination: List[str] = []

    def log(message: str) -> None:
        print(f"[ProducerConsumer] {message}")

    log(
        "Config -> items=%s buffer_capacity=%s producers=%s consumers=%s delay=%.2fs"
        % (item_count, buffer_capacity, producer_count, consumer_count, delay_seconds)
    )

    producers: List[Producer[object]] = []
    for index, group in enumerate(item_groups, start=1):
        producer = Producer(
            buffer=buffer,
            source=group,
            sentinel=None,
            delay_seconds=delay_seconds,
        )
        producer.name = f"Producer-{index}"
        producers.append(producer)

    sentinel = object()
    consumers: List[Consumer[object]] = []
    for index in range(consumer_count):
        consumer = Consumer(
            buffer=buffer,
            destination=destination,
            sentinel=sentinel,
            on_item=lambda item, idx=index: log(
                f"Consumer-{idx + 1} received item='{item}' (buffer size {buffer.current_size()})"
            ),
        )
        consumer.name = f"Consumer-{index + 1}"
        consumers.append(consumer)

    log("Launching threads...")
    for worker in (*producers, *consumers):
        worker.start()

    for producer in producers:
        producer.join()

    for _ in consumers:
        buffer.put(sentinel)

    for consumer in consumers:
        consumer.join()

    log(f"Produced {len(items)} items; destination now has {len(destination)} items")
    log(f"Consumed sequence: {destination}")

    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Producer-consumer demo runner")
    parser.add_argument("--items", type=int, default=8, help="total number of items to produce")
    parser.add_argument("--buffer-capacity", type=int, default=4, help="bounded buffer capacity")
    parser.add_argument("--producers", type=int, default=1, help="number of producer threads")
    parser.add_argument("--consumers", type=int, default=1, help="number of consumer threads")
    parser.add_argument(
        "--delay",
        type=float,
        default=0.01,
        help="artificial delay (seconds) between producer puts to visualize concurrency",
    )
    args = parser.parse_args()
    run_demo(
        item_count=args.items,
        buffer_capacity=args.buffer_capacity,
        producer_count=max(1, args.producers),
        consumer_count=max(1, args.consumers),
        delay_seconds=max(0.0, args.delay),
    )


if __name__ == "__main__":
    main()

