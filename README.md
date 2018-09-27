# pymessagebus

<h2 align="center">a Message/Command Bus for Python</h2>

<p align="center">
<a href="https://travis-ci.org/DrBenton/pymessagebus"><img alt="Build Status" src="https://travis-ci.org/DrBenton/pymessagebus.svg?branch=master"></a>
<a href='https://coveralls.io/github/DrBenton/pymessagebus?branch=master'><img src="https://coveralls.io/repos/github/DrBenton/pymessagebus/badge.svg?branch=master" alt="Coverage Status" /></a>
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

Pymessagebus is a message bus library. It comes with a generic MessageBus class, as well as a more specialised CommandBus one.

_N.B.: here the "Message Bus" / "Command Bus" terms refer to a design patterns, and have nothing to do with messaging systems like RabbitMQ. (even though they can be used together)_

I created it because I've been using this design pattern for years while working on Symfony applications, and it never disappointed me - it's really a pretty simple and efficient way to decouple the business actions from their implementations.

You can have a look at the following URLs to learn more about this design pattern:

- https://matthiasnoback.nl/2015/01/a-wave-of-command-buses/ - a great series of articles explaining the design pattern - it uses PHP but that doesn't matter, the pattern is the same whatever the language is :-)
- http://tactician.thephpleague.com/ - this is a pretty good and pragamatic PHP implementation of the CommandBus pattern, with clear explanations about the pattern
- http://docs.simplebus.io/en/latest/ - another excellent PHP implementation, a bit more pure since sending Commands on the CommandBus can't return values here. _(my personal experience is that it's often handy to be able to return something from the execution of a COmmand, even if it's a bit less pure)_
- https://en.wikipedia.org/wiki/Command_pattern

## Install

```bash
$ pip install "pymessagebus==1.*"
```

## Synopsis

A naive example of how the CommandBus allows one to keep the business actions (Commands) decoupled from the implementation of their effect (the Command Handlers):

```python
# domain.py
import typing as t

class CreateCustomerCommand(t.NamedTuple):
    first_name: str
    last_name: str

# command_handlers.py
import domain

def handle_customer_creation(command: domain.CreateCustomerCommand) -> int:
    customer = OrmCustomer()
    customer.full_name = f"{command.first_name} {command.last_name}"
    customer.creation_date = datetime.now()
    customer.save()
    return customer.id

# command_bus.py
command_bus = CommandBus()
command_bus.add_handler(CreateCustomerCommand, handle_customer_creation)

# api.py
import domain
from command_bus import command_bus

@post("/customer)
def post_customer(params):
    # Note that the implmentation (the "handle_customer_creation" function)
    # is completely invisible here, we only know about the (agnostic) CommandBus
    # and the class that describe the business action (the Command)
    command  = CreateCustomerCommand(params["first_name"], params["last_name"])
    customer_id = command_bus.handle(command)
    return customer_id
```

## API

#### MessageBus

The `MessageBus` class allows one to trigger one or multiple handlers when a
message of a given type is sent on the bus.  
The result is an array of results, where each item is the result of one the handlers execution.

```python
class BusinessMessage(t.NamedTuple):
    payload: int

def handler_one(message: BusinessMessage):
    return f"handler one result: {message.payload}"

def handler_two(message: BusinessMessage):
    return f"handler two result: {message.payload}"

message_bus = MessageBus()
message_bus.add_handler(BusinessMessage, handler_one)
message_bus.add_handler(BusinessMessage, handler_two)

message = BusinessMessage(payload=33)
result = message_bus.handle(message)
# result = ["handler one result: 33", "handler one result: 34"]
```

The API is therefore pretty straightforward (you can see it as an abstract class in the [api](/pymessagebus/api.py) module):

- `add_handler(message_class: type, message_handler: t.Callable) -> None` adds a handler, that will be triggered by the instance of the bus when a message of this class is sent to it.
- `handle(message: object) -> t.List[t.Any]` trigger the handler(s) previously registered for that message class. If no handler has been registered for this kind of message, an empty list is returned.
- `has_handler_for(message_class: type) -> bool` just allows one to check if one or more handlers have been registered for a given message class.

#### CommandBus

The `CommandBus` is a specialised version of a `MessageBus` (technically it's just a proxy on top of a MessageBus, which adds the management of those specificities), which comes with the following subtleties:

- Only one handler can be registered for a given message class
- When a message is sent to the bus via the `handle` method, an error will be raised if no handler has been registered for this message class.

**In short, a Command Bus assumes that it's mandatory to a handler triggered for every business action we send on it - an to have only one.**

The API is thus exactly the same than the MessageBus, with the following technical differences:

- the `add_handler(message_class, handler)` method will raise a `api.CommandHandlerAlreadyRegisteredForATypeError` exception if one tries to register a handler for a class of message for which another handler has already been registered before.
- the `handle(message)` method returns a single result rather than a list of result (as we can - and must - have only one single handler for a given message class). If no handler has been registered for this message class, a `api.CommandHandlerNotFoundError` exception is raised.

##### Additional options for the CommandBus

The CommandBus constructor have additional options that you can use to customise its behaviour:

- `allow_result`: it's possible to be stricter about the implementation of the CommandBus pattern, by using the `allow_result=True` named parameter when the class is instanciated (the default value being `False`).  
  In that case the result of the `handle(message)` will always be `None`. By doing this one can follow a more pure version of the design pattern. (and access the result of the Command handling via the application repositories, though a pre-generated id attached to the message for example)
- `locking`: by default the CommandBus will raise a `api.CommandBusAlreadyRunningAMessageError` exception if a message is sent to it while another message is still processed (which can happen if one of the Command Handlers sends a message to the bus).  
  You can disable this behaviour by setting the named argument `locking=False` (the default value being `True`).

#### Middlewares

Last but not least, both kinds of buses can accept Middlewares.

A Middleware is a function that receives a message (sent to the bus) as its first argument and a "next_middleware" function as second argument. That function can do some custom processing before or/and after the next Middleware (or the execution of the handler(s) registered for that kind of message) is triggered.

Middlewares are triggered in a "onion shape": in the case of 2 Middlweares for example:

- the first registered Middleware "pre-processing" will be executed first
- the second one will come after
- then the handler(s) registed for that message class is executed (it's the core of the onion)

And then we get out of the onion in the opposite direction:

- the second Middleware "post-processing" takes place
- the first Middleware "post-processing" is triggered
- the result if finally returned

Middlewares can change the message sent to the next Middlewares (or to the message handler(s)), but they can also perform some processing that doesn't affect the message (like logging for instance).

Here is a snippet illustrating this:

```python
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
```

#### Logging middleware

For convenience a "logging" middleware comes with the package.

Synopis

```python
import logging
from pymessagebus.middleware.logger import get_logger_middleware

logger = logging.getLogger("message_bus")
logging_middleware = get_logger_middleware(logger)

message_bus = MessageBus(middlewares=[logging_middleware])

# Now you will get logging messages:
#  - when a message is sent on the bus (default logging level: DEBUG)
#  - when a message has been successfully handled by the bus, with no Exception raised (default logging level: DEBUG)
#  - when the processing of a message has raised an Exception (default logging level: ERROR)
```

You can customise the logging levels of the middleware via the `LoggingMiddlewareConfig` class:

```python
import logging
from pymessagebus.middleware.logger import get_logger_middleware, LoggingMiddlewareConfig

logger = logging.getLogger("message_bus")
logging_middleware_config = LoggingMiddlewareConfig(
    mgs_received_level=logging.INFO,
    mgs_succeeded_level=logging.INFO,
    mgs_failed_level=logging.CRITICAL
)
logging_middleware = get_logger_middleware(logger, logging_middleware_config)
```

### "default" singletons

Because most of the use cases of those buses rely on a single instance of the bus, for commodity you can also use singletons for both the MessageBus and CommandBus, accessible from a "default" subpackage.

These versions also expose a very handy `register_handler(message_class: type)` decorator.

Synopsis:

```python
# domain.py
import typing as t

class CreateCustomerCommand(t.NamedTuple):
    first_name: str
    last_name: str

# command_handlers.py
from pymessagebus.default import commandbus
import domain

@commandbus.register_handler(domain.CreateCustomerCommand)
def handle_customer_creation(command) -> int:
    customer = OrmCustomer()
    customer.full_name = f"{command.first_name} {command.last_name}"
    customer.creation_date = datetime.now()
    customer.save()
    return customer.id

# api.py
from pymessagebus.default import commandbus
import domain

@post("/customer)
def post_customer(params):
    # Note that the implmentation (the "handle_customer_creation" function)
    # is completely invisible here, we only know about the (agnostic) CommandBus
    # and the class that describe the business action (the Command)
    command  = CreateCustomerCommand(params["first_name"], params["last_name"])
    customer_id = command_bus.handle(command)
    return customer_id
```

You can notice that the difference with the first synopsis is that here we don't have to instantiate the CommandBus, and that the `handle_customer_creation` function is registered to it automatically by using the decorator.

## Code quality

The code itself is formatted with Black and checked with PyLint and MyPy.

The whole package comes with a full test suite, managed by PyTest.

```bash
$ make test
```
