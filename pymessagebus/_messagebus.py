from collections import defaultdict
import typing as t

import pymessagebus.api as api


class MessageBus(api.MessageBus):
    def __init__(self) -> None:
        self._handlers: t.Dict[type, t.List[t.Callable]] = defaultdict(list)

    def add_handler(self, message_class: type, message_handler: t.Callable) -> None:
        if not isinstance(message_class, type):
            raise api.MessageHandlerMappingRequiresATypeError(
                f"add_handler() first argument must be a type, got '{type(message_class)}"
            )
        if not callable(message_handler):
            raise api.MessageHandlerMappingRequiresACallableError(
                f"add_handler() second argument must be a callable, got '{type(message_handler)}"
            )

        self._handlers[message_class].append(message_handler)

    def handle(self, message: object) -> t.List[t.Any]:
        if not self.has_handler_for(message.__class__):
            return []
        handlers: t.List[t.Callable] = self._handlers[message.__class__]
        results = [self._trigger_handler(message, handler) for handler in handlers]
        return results

    def has_handler_for(self, message_class: type) -> bool:
        return message_class in self._handlers

    @staticmethod
    def _trigger_handler(message: object, handler: t.Callable) -> t.Any:
        return handler(message)
