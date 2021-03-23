from collections import defaultdict
import typing as t

from . import api


class MessageBus(api.MessageBus):
    def __init__(self, *, middlewares: t.List[api.Middleware] = None) -> None:
        self._handlers: t.Dict[type, t.List[t.Callable]] = defaultdict(list)
        self._middlewares_chain = self._get_middlewares_callables_chain(
            middlewares, self._trigger_handlers_for_message_as_a_middleware
        )

    def add_handler(self, message_class: type, message_handler: t.Callable) -> None:
        if not isinstance(message_class, type):
            raise api.MessageHandlerMappingRequiresAType(
                f"add_handler() first argument must be a type, got '{type(message_class)}"
            )
        if not callable(message_handler):
            raise api.MessageHandlerMappingRequiresACallable(
                f"add_handler() second argument must be a callable, got '{type(message_handler)}"
            )

        self._handlers[message_class].append(message_handler)

    def remove_handler(self, message_class: type, message_handler: t.Callable) -> bool:
        """
        Returns `True` if a handler was found for this message class and caller and removed,
        `False` otherwise
        """
        if not isinstance(message_class, type):
            raise api.MessageHandlerMappingRequiresAType(
                f"add_handler() first argument must be a type, got '{type(message_class)}"
            )
        if not callable(message_handler):
            raise api.MessageHandlerMappingRequiresACallable(
                f"add_handler() second argument must be a callable, got '{type(message_handler)}"
            )
        if message_class not in self._handlers:
            return False
        if message_handler not in self._handlers[message_class]:
            return False

        self._handlers[message_class].remove(message_handler)

        if len(self._handlers[message_class]) == 0:
            del self._handlers[message_class]

        return True

    def handle(self, message: object) -> t.List[t.Any]:
        if not self.has_handler_for(message.__class__):
            return []
        result = self._middlewares_chain(message)
        return result

    def has_handler_for(self, message_class: type) -> bool:
        return message_class in self._handlers

    def _trigger_handlers_for_message_as_a_middleware(
        self, message: object, unused_next: t.Callable
    ) -> t.List[t.Any]:
        handlers: t.List[t.Callable] = self._handlers[message.__class__]
        results = [self._trigger_handler(message, handler) for handler in handlers]
        return results

    @staticmethod
    def _get_middlewares_callables_chain(
        middlewares: t.Union[t.List[api.Middleware], None], message_handler: t.Callable
    ) -> t.Callable[[object], t.Any]:
        """
        The algorithm comes from the source code of Tactician (PHP CommandBus):
        https://github.com/thephpleague/tactician/blob/master/src/CommandBus.php#L50 :-)
        """
        all_middlewares = (middlewares or []) + [message_handler]

        # the last "middleware" is actually the execution of the target Message Handler,
        # so it won't make any use of the "next" parameter but we have to provide it.
        # --> let's use a no-op lambda as the last middleware's "next" parameter:
        chain = lambda _: None

        for middleware in reversed(all_middlewares):
            chain = MessageBus._get_middleware_callable_for_middleware(
                middleware, chain
            )
        return chain

    @staticmethod
    def _get_middleware_callable_for_middleware(
        middleware: api.Middleware, next_middleware: t.Callable
    ) -> t.Callable[[object], t.Any]:
        def middleware_callable(message: object):
            return middleware(message, next_middleware)

        return middleware_callable

    @staticmethod
    def _trigger_handler(message: object, handler: t.Callable) -> t.Any:
        return handler(message)
