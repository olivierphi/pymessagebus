# pylint: skip-file

import importlib
from contextlib import contextmanager
import typing as t

import pytest

from pymessagebus.api import CommandHandlerAlreadyRegisteredForAType


@contextmanager
def _default_commandbus_unloaded_after_test():
    # Since our "default" CommandBus is just a convenient singleton with a handy decorator,
    # we have to reload it everytime we finish a test (or we will find the previous used one for the next test)
    from pymessagebus.default import commandbus as default_commandbus

    try:
        yield default_commandbus
    finally:
        importlib.reload(default_commandbus)


# Since this "default" package is just a convenient wrapper around our (already tested) MessageBus,
# we won't test everything again :-)
# Let's focus on its first specificity: the singleton aspect!


def test_its_well_and_truly_a_singleton():
    with _default_commandbus_unloaded_after_test():

        def test1():
            def handler(msg):
                return 10

            from pymessagebus.default import commandbus as default_commandbus

            default_commandbus.add_handler(EmptyMessage, handler)
            message = EmptyMessage()

            handling_result = default_commandbus.handle(message)
            assert handling_result == 10

        test1()

        def test2():
            def handler(msg):
                return 20

            from pymessagebus.default import commandbus as default_commandbus

            # Now we should trigger an error, since we're re-using the same singleton:
            with pytest.raises(CommandHandlerAlreadyRegisteredForAType):
                default_commandbus.add_handler(EmptyMessage, handler)

        test2()


# Let's now focus on its second specificity: the decorator!


def test_simplest_decorator():
    with _default_commandbus_unloaded_after_test() as sut:

        @sut.register_handler(EmptyMessage)
        def handler(msg):
            return "decorated"

        message = EmptyMessage()
        handling_result = sut.handle(message)
        assert handling_result == "decorated"


def test_decorator_receives_message():
    with _default_commandbus_unloaded_after_test() as sut:

        class MessageWithPayload(t.NamedTuple):
            number: int

        @sut.register_handler(MessageWithPayload)
        def add_five(msg):
            return msg.number + 5

        message = MessageWithPayload(number=3)
        handling_result = sut.handle(message)
        assert handling_result == 8
        message = MessageWithPayload(number=18)
        handling_result = sut.handle(message)
        assert handling_result == 23


def test_multiple_decorators():
    with _default_commandbus_unloaded_after_test() as sut:

        @sut.register_handler(MessageClassOne)
        def handler_one(msg):
            return 1

        @sut.register_handler(MessageClassTwo)
        def handler_two(msg):
            return 2

        message_one = MessageClassOne()
        handling_result = sut.handle(message_one)
        assert handling_result == 1

        message_two = MessageClassTwo()
        handling_result = sut.handle(message_two)
        assert handling_result == 2


def test_multiple_decorators_for_same_message_type_triggers_an_error():
    with _default_commandbus_unloaded_after_test() as sut:

        @sut.register_handler(MessageClassOne)
        def handler_one(msg):
            return 1

        with pytest.raises(CommandHandlerAlreadyRegisteredForAType):

            @sut.register_handler(MessageClassOne)
            def handler_two(msg):
                return 2


class EmptyMessage:
    pass


class MessageClassOne:
    pass


class MessageClassTwo:
    pass
