from abc import ABC, abstractmethod
import typing as t

CallNextMiddleware = t.Callable[[object], t.Any]
Middleware = t.Callable[[object, CallNextMiddleware], t.Any]


class MessageBus(ABC):
    @abstractmethod
    def add_handler(self, message_class: type, message_handler: t.Callable) -> None:
        pass

    @abstractmethod
    def remove_handler(self, message_class: type, message_handler: t.Callable) -> bool:
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
    def remove_handler(self, message_class: type) -> bool:
        pass

    @abstractmethod
    def handle(self, message: object) -> None:
        pass

    @abstractmethod
    def has_handler_for(self, message_class: type) -> bool:
        pass


class MessageBusError(Exception, ABC):
    pass


class MessageHandlerMappingRequiresAType(MessageBusError):
    pass


class MessageHandlerMappingRequiresACallable(MessageBusError):
    pass


class CommandHandlerNotFound(MessageBusError):
    pass


class CommandHandlerAlreadyRegisteredForAType(MessageBusError):
    pass


class CommandBusAlreadyProcessingAMessage(MessageBusError):
    pass
