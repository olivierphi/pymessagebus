from abc import ABC
from collections import defaultdict
import typing as t


class MessageHandlerNotFoundError(KeyError):
    pass


class MessageBus:
    def __init__(self) -> None:
        self._handlers: t.Dict[type, t.List[t.Callable]] = defaultdict(list)

    def add_handler(self, message_class: type, message_handler: t.Callable) -> None:
        self._handlers[message_class].append(message_handler)

    def handle(self, message: object) -> t.List[t.Any]:
        if not self.has_handler_for(message.__class__):
            raise MessageHandlerNotFoundError(
                f"No handler found for message class '{message.__class__}''"
            )
        handlers = self._handlers[message.__class__]
        results = []
        for handler in handlers:
            results.append(self._trigger_handler(message, handler))
        return results

    def has_handler_for(self, message_class: type) -> bool:
        return message_class in self._handlers

    @staticmethod
    def _trigger_handler(message: object, handler: t.Callable) -> t.Any:
        return handler(message)
