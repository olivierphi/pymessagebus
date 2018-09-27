# pylint:  skip-file
import typing as t

import pytest

from pymessagebus import api
from pymessagebus._messagebus import MessageBus


def test_simplest_handler_can_have_no_handlers_for_a_message():
    sut = MessageBus()

    message = EmptyMessage()
    handling_result = sut.handle(message)
    assert handling_result == []


def test_simplest_handler():
    sut = MessageBus()
    sut.add_handler(EmptyMessage, get_one)

    message = EmptyMessage()
    handling_result = sut.handle(message)
    assert handling_result == [1]


def test_has_handler_for():
    sut = MessageBus()
    sut.add_handler(MessageClassOne, get_one)

    assert sut.has_handler_for(MessageClassOne) is True
    assert sut.has_handler_for(MessageClassTwo) is False


def test_handlers_get_message():
    sut = MessageBus()
    sut.add_handler(EmptyMessage, identity_handler)

    message = EmptyMessage()
    handling_result = sut.handle(message)
    assert handling_result == [message]


def test_handler_message_must_be_a_type():
    sut = MessageBus()

    not_a_type = EmptyMessage()
    with pytest.raises(api.MessageHandlerMappingRequiresATypeError):
        sut.add_handler(not_a_type, get_one)


def test_handler_handler_must_be_a_callable():
    sut = MessageBus()

    not_a_callable = 2
    with pytest.raises(api.MessageHandlerMappingRequiresACallableError):
        sut.add_handler(EmptyMessage, not_a_callable)


def test_multiple_handlers_for_single_message():
    sut = MessageBus()
    sut.add_handler(EmptyMessage, get_one)
    sut.add_handler(EmptyMessage, get_one)

    message = EmptyMessage()
    handling_result = sut.handle(message)
    assert handling_result == [1, 1]


def test_multiple_handlers_for_single_message_triggered_in_correct_order():
    sut = MessageBus()
    sut.add_handler(EmptyMessage, get_one)
    sut.add_handler(EmptyMessage, get_two)
    sut.add_handler(EmptyMessage, get_three)

    message = EmptyMessage()
    handling_result = sut.handle(message)
    assert handling_result == [1, 2, 3]


def test_multiple_handlers_correctly_triggered():
    sut = MessageBus()
    sut.add_handler(MessageClassOne, get_one)
    sut.add_handler(MessageClassOne, get_two)
    sut.add_handler(MessageClassTwo, get_three)

    message_one = MessageClassOne()
    handling_result_one = sut.handle(message_one)
    assert handling_result_one == [1, 2]

    message_two = MessageClassTwo()
    handling_result_two = sut.handle(message_two)
    assert handling_result_two == [3]


def test_handler_is_triggered_each_time():
    counter = 0

    def handler(msg):
        nonlocal counter
        counter += 1
        return counter

    sut = MessageBus()
    sut.add_handler(EmptyMessage, handler)

    message = EmptyMessage()
    handling_result = sut.handle(message)
    assert handling_result == [1]
    handling_result = sut.handle(message)
    assert handling_result == [2]


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

    def handler_one(message: MessageWithList):
        message.payload.append("handler one does something")
        return "handler one result"

    def handler_two(message: MessageWithList):
        message.payload.append("handler two does something")
        return "handler two result"

    # 1. Simplest test: one handler, one middleware
    sut1 = MessageBus(middleswares=[middleware_one])
    sut1.add_handler(MessageWithList, handler_one)

    message1 = MessageWithList(payload=[])
    result1 = sut1.handle(message1)
    assert result1 == ["handler one result"]
    assert message1.payload == [
        "middleware one: does something before the handler",
        "handler one does something",
        "middleware one: does something after the handler",
    ]

    # 2. Next step: one handler, multiple middlewares
    sut2 = MessageBus(middleswares=[middleware_one, middleware_two])
    sut2.add_handler(MessageWithList, handler_one)

    message2 = MessageWithList(payload=[])
    result2 = sut2.handle(message2)
    assert result2 == ["handler one result"]
    assert message2.payload == [
        "middleware one: does something before the handler",
        "middleware two: does something before the handler",
        "handler one does something",
        "middleware two: does something after the handler",
        "middleware one: does something after the handler",
    ]

    # 3. Ultimate step: multiple handlers, multiple middlewares
    sut3 = MessageBus(middleswares=[middleware_one, middleware_two])
    sut3.add_handler(MessageWithList, handler_one)
    sut3.add_handler(MessageWithList, handler_two)

    message3 = MessageWithList(payload=["initial message payload"])
    result3 = sut3.handle(message3)
    assert result3 == ["handler one result", "handler two result"]
    assert message3.payload == [
        "initial message payload",
        "middleware one: does something before the handler",
        "middleware two: does something before the handler",
        "handler one does something",
        "handler two does something",
        "middleware two: does something after the handler",
        "middleware one: does something after the handler",
    ]


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
