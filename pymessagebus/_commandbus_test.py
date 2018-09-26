# pylint: skip-file
import typing as t

import pytest

from pymessagebus import api
from pymessagebus._commandbus import CommandBus


def test_simplest_handler():
    sut = CommandBus()
    sut.add_handler(EmptyMessage, get_one)

    message = EmptyMessage()
    handling_result = sut.handle(message)
    assert handling_result == 1


def test_has_handler_for():
    sut = CommandBus()
    sut.add_handler(MessageClassOne, get_one)

    assert sut.has_handler_for(MessageClassOne) is True
    assert sut.has_handler_for(MessageClassTwo) is False


def test_commandbus_can_be_configured_to_not_return_anything_on_command_handling():
    sut = CommandBus(allow_result=False)
    sut.add_handler(MessageClassOne, get_one)

    message = MessageClassOne()
    handling_result = sut.handle(message)
    assert handling_result is None


def test_handlers_get_message():
    sut = CommandBus()
    sut.add_handler(EmptyMessage, identity_handler)

    message = EmptyMessage()
    handling_result = sut.handle(message)
    assert handling_result == message


def test_handler_must_be_registered_for_a_message_type():
    sut = CommandBus()

    message = EmptyMessage()
    with pytest.raises(api.CommandHandlerNotFoundError):
        sut.handle(message)


def test_handler_message_must_be_a_type():
    sut = CommandBus()

    not_a_type = EmptyMessage()
    with pytest.raises(api.MessageHandlerMappingRequiresATypeError):
        sut.add_handler(not_a_type, get_one)


def test_multiple_handlers_for_single_message_triggers_error():
    sut = CommandBus()
    sut.add_handler(EmptyMessage, get_one)

    with pytest.raises(api.CommandHandlerAlreadyRegisteredForATypeError):
        sut.add_handler(EmptyMessage, get_one)


def test_handler_is_triggered_each_time():
    counter = 0

    def handler(msg):
        nonlocal counter
        counter += 1
        return counter

    sut = CommandBus()
    sut.add_handler(EmptyMessage, handler)

    message = EmptyMessage()
    handling_result = sut.handle(message)
    assert handling_result == 1
    handling_result = sut.handle(message)
    assert handling_result == 2


def test_middlewares():
    class MessageWithList(t.NamedTuple):
        payload: t.List[str]

    def middleware_one(message: MessageWithList, next: api.CallNextMiddleware):
        message.payload.append("middleware one: does something before the handler")
        result = next(message)
        message.payload.append("middleware one: does something after the handler")
        return result

    def middleware_two(message: MessageWithList, next: api.CallNextMiddleware):
        message.payload.append("middleware two: does something before the handler")
        result = next(message)
        message.payload.append("middleware two: does something after the handler")
        return result

    def handler(message: MessageWithList) -> str:
        message.payload.append("handler does something")
        return "handler result"

    # We already tests simpler cases on the MessageBus test suite, so we will only test the most complex case here:
    sut = CommandBus(middleswares=[middleware_one, middleware_two])
    sut.add_handler(MessageWithList, handler)

    message = MessageWithList(payload=["initial message payload"])
    result = sut.handle(message)
    assert message.payload == [
        "initial message payload",
        "middleware one: does something before the handler",
        "middleware two: does something before the handler",
        "handler does something",
        "middleware two: does something after the handler",
        "middleware one: does something after the handler",
    ]
    assert result == "handler result"


class EmptyMessage:
    pass


class MessageClassOne:
    pass


class MessageClassTwo:
    pass


def identity_handler(message: object) -> object:
    return message


get_one = lambda _: 1
get_two = lambda _: 2
get_three = lambda _: 3
