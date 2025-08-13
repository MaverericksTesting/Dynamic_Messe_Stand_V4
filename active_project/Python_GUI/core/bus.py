# core/bus.py
"""
Event-Bus für lose Kopplung zwischen Komponenten
"""
from collections import defaultdict
from typing import Callable, Dict, List, Any

class EventBus:
    """Framework-agnostischer Event-Bus für Publish/Subscribe Pattern"""
    
    def __init__(self):
        self._subs: Dict[str, List[Callable[..., None]]] = defaultdict(list)

    def subscribe(self, topic: str, fn: Callable[..., None]) -> None:
        """Event-Handler für Topic registrieren"""
        self._subs[topic].append(fn)

    def unsubscribe(self, topic: str, fn: Callable[..., None]) -> None:
        """Event-Handler entfernen"""
        if topic in self._subs and fn in self._subs[topic]:
            self._subs[topic].remove(fn)

    def publish(self, topic: str, **payload: Any) -> None:
        """Event mit Payload an alle Subscriber senden"""
        for fn in list(self._subs.get(topic, [])):
            try:
                fn(**payload)
            except Exception as e:
                print(f"❌ Event-Handler Fehler für '{topic}': {e}")

# Globale Event-Bus Instanz
bus = EventBus()