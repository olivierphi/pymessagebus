import typing as t

from pymessagebus._commandbus import CommandBus


_DEFAULT_COMMAND_BUS = CommandBus()

# Public API:
# This is our handy decorator:
def register_handler(message_class: type):
    def decorator(handler: t.Callable):
        _DEFAULT_COMMAND_BUS.add_handler(message_class, handler)
        return handler

    return decorator


# And those are aliases to our "default" singleton instance:
# pylint: disable=invalid-name
add_handler = _DEFAULT_COMMAND_BUS.add_handler
handle = _DEFAULT_COMMAND_BUS.handle
has_handler_for = _DEFAULT_COMMAND_BUS.has_handler_for
