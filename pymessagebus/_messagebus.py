from abc import ABC
from collections import defaultdict
import typing as t


class MessageHandlerNotFoundError(KeyError):
    pass


class MessageBus:
    def __init__(self) -> None:
        self._handlers: t.Dict[object, t.List[t.Callable]] = defaultdict(list)

    def add_handler(self, message_class: object, message_handler: t.Callable) -> None:
        self._handlers[message_class].append(message_handler)

    def handle(self, message: object) -> t.List[t.Any]:
        if message.__class__ not in self._handlers:
            raise MessageHandlerNotFoundError(
                f"No handler found for message class '{message.__class__}''"
            )
        handlers = self._handlers[message.__class__]
        results = []
        for handler in handlers:
            results.append(self._trigger_handler(message, handler))
        return results

    @staticmethod
    def _trigger_handler(message: object, handler: t.Callable) -> t.Any:
        return handler(message)
