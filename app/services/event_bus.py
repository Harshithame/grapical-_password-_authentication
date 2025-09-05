from __future__ import annotations

import threading
from collections import defaultdict
from typing import Callable, Dict, List, Any


class EventBus:
    """A minimal in-process pub/sub event bus."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[[dict], None]]] = defaultdict(list)
        self._lock = threading.RLock()

    def subscribe(self, event_name: str, handler: Callable[[dict], None]) -> None:
        with self._lock:
            self._subscribers[event_name].append(handler)

    def publish(self, event_name: str, payload: dict) -> None:
        # Copy handlers to avoid mutation during iteration
        with self._lock:
            handlers = list(self._subscribers.get(event_name, []))
        for handler in handlers:
            try:
                handler(payload)
            except Exception:
                # Fail-safe: do not let handlers crash the bus
                pass


global_event_bus = EventBus()
