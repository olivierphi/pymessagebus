import typing as t

from ._messagebus import api, MessageBus


class CommandBus(api.CommandBus):
    def __init__(
        self,
        *,
        middlewares: t.List[api.Middleware] = None,
        allow_result: bool = True,
        locking: bool = True,
    ) -> None:
        self._messagebus = MessageBus(middlewares=middlewares)
        self._allow_result = bool(allow_result)
        self._locking = bool(locking)
        self._is_processing_a_message = False

    def add_handler(self, message_class: type, message_handler: t.Callable) -> None:
        if self._messagebus.has_handler_for(message_class):
            raise api.CommandHandlerAlreadyRegisteredForAType(
                f"A command handler is already registed for message class '{message_class}'."
            )
        self._messagebus.add_handler(message_class, message_handler)

    def remove_handler(self, message_class: type) -> bool:
        if not self._messagebus.has_handler_for(message_class):
            return False
        return self._messagebus.remove_handler(
            message_class, self._messagebus._handlers[message_class][0]
        )

    def handle(self, message: object) -> t.Any:
        if not self._messagebus.has_handler_for(message.__class__):
            raise api.CommandHandlerNotFound(
                f"No command handler is registered for message class '{message.__class__}'."
            )
        if self._locking and self._is_processing_a_message:
            raise api.CommandBusAlreadyProcessingAMessage(
                f"CommandBus already processing a message when received a '{message.__class__}' one."  # pylint: disable=line-too-long
            )
        self._is_processing_a_message = True
        result = self._messagebus.handle(message)
        self._is_processing_a_message = False
        return result[0] if self._allow_result else None

    def has_handler_for(self, message_class: type) -> bool:
        return self._messagebus.has_handler_for(message_class)
