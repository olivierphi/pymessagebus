# pylint: skip-file


def test_messagebus_package_alias():
    from pymessagebus import MessageBus

    sut = MessageBus()
    sut.add_handler(EmptyMessage, get_one)
    sut.add_handler(EmptyMessage, get_two)

    message = EmptyMessage()
    handling_result = sut.handle(message)
    assert handling_result == [1, 2]


def test_commandbus_package_alias():
    from pymessagebus import CommandBus

    sut = CommandBus()
    sut.add_handler(EmptyMessage, get_one)

    message = EmptyMessage()
    handling_result = sut.handle(message)
    assert handling_result == 1


class EmptyMessage:
    pass


get_one = lambda _: 1
get_two = lambda _: 2
