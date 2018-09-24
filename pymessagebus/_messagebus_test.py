# pylint:  skip-file

import pytest

from pymessagebus.api import MessageHandlerMappingRequiresATypeError
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


def test_handler_is_not_a_type():
    sut = MessageBus()

    with pytest.raises(MessageHandlerMappingRequiresATypeError):
        sut.add_handler(EmptyMessage(), get_one)


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
