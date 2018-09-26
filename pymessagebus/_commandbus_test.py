# pylint: skip-file

import pytest

from pymessagebus._commandbus import CommandBus
from pymessagebus.api import (
    CommandHandlerAlreadyRegisteredForATypeError,
    CommandHandlerNotFoundError,
    MessageHandlerMappingRequiresATypeError,
)


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


def test_handlers_get_message():
    sut = CommandBus()
    sut.add_handler(EmptyMessage, identity_handler)

    message = EmptyMessage()
    handling_result = sut.handle(message)
    assert handling_result == message


def test_handler_must_be_registered_for_a_message_type():
    sut = CommandBus()

    message = EmptyMessage()
    with pytest.raises(CommandHandlerNotFoundError):
        sut.handle(message)


def test_handler_message_must_be_a_type():
    sut = CommandBus()

    not_a_type = EmptyMessage()
    with pytest.raises(MessageHandlerMappingRequiresATypeError):
        sut.add_handler(not_a_type, get_one)


def test_multiple_handlers_for_single_message_triggers_error():
    sut = CommandBus()
    sut.add_handler(EmptyMessage, get_one)

    with pytest.raises(CommandHandlerAlreadyRegisteredForATypeError):
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
