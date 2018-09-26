from abc import ABC, abstractmethod
import typing as t

CallNextMiddleware = t.Callable[[object], t.Any]
Middleware = t.Callable[[object, CallNextMiddleware], t.Any]


class MessageBus(ABC):
    @abstractmethod
    def add_handler(self, message_class: type, message_handler: t.Callable) -> None:
        pass

    @abstractmethod
    def handle(self, message: object) -> t.List[t.Any]:
        pass

    @abstractmethod
    def has_handler_for(self, message_class: type) -> bool:
        pass


class CommandBus(ABC):
    @abstractmethod
    def add_handler(self, message_class: type, message_handler: t.Callable) -> None:
        pass

    @abstractmethod
    def handle(self, message: object) -> None:
        pass

    @abstractmethod
    def has_handler_for(self, message_class: type) -> bool:
        pass


class MessageBusError(BaseException):
    pass


class MessageHandlerMappingRequiresATypeError(MessageBusError):
    pass


class MessageHandlerMappingRequiresACallableError(MessageBusError):
    pass


class CommandHandlerNotFoundError(MessageBusError):
    pass


class CommandHandlerAlreadyRegisteredForATypeError(MessageBusError):
    pass
