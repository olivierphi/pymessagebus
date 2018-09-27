import typing as t

from pymessagebus._messagebus import MessageBus


_DEFAULT_MESSAGE_BUS = MessageBus()

# Public API:
# This is our handy decorator:
def register_handler(message_class: type):
    def decorator(handler: t.Callable):
        _DEFAULT_MESSAGE_BUS.add_handler(message_class, handler)
        return handler

    return decorator


# And those are aliases to our "default" singleton instance:
# pylint: disable=invalid-name
add_handler = _DEFAULT_MESSAGE_BUS.add_handler
handle = _DEFAULT_MESSAGE_BUS.handle
has_handler_for = _DEFAULT_MESSAGE_BUS.has_handler_for
