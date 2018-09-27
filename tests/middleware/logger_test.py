# pylint: skip-file

import logging
import random

import pytest

from pymessagebus import MessageBus
from pymessagebus.middleware.logger import (
    get_logger_middleware,
    LoggingMiddlewareConfig,
)


def test_middleware_basic(caplog):
    logger_name = f"{__name__}.{random.randint(1000, 9999)}"
    logger = logging.getLogger(logger_name)

    sut = get_logger_middleware(logger)
    message_bus = MessageBus(middleswares=[sut])
    message_bus.add_handler(MessageClassOne, get_one)

    message = MessageClassOne()
    with caplog.at_level(logging.DEBUG, logger=logger_name):
        result = message_bus.handle(message)
        assert result == [1]
        log_records = caplog.records

        assert len(log_records) == 2
        assert (
            log_records[0].msg
            == "Message received: $<class 'logger_test.MessageClassOne'>"
        )
        assert log_records[0].levelno == logging.DEBUG
        assert (
            log_records[1].msg
            == "Message succeeded: $<class 'logger_test.MessageClassOne'>"
        )
        assert log_records[1].levelno == logging.DEBUG


def test_middleware_with_error(caplog):
    logger_name = f"{__name__}.{random.randint(1000, 9999)}"
    logger = logging.getLogger(logger_name)

    sut = get_logger_middleware(logger)
    message_bus = MessageBus(middleswares=[sut])
    message_bus.add_handler(MessageClassOne, errorful_handler)
    message = MessageClassOne()
    with caplog.at_level(logging.DEBUG, logger=logger_name):
        with pytest.raises(RuntimeError):
            message_bus.handle(message)
        log_records = caplog.records

        assert len(log_records) == 2
        assert (
            log_records[0].msg
            == "Message received: $<class 'logger_test.MessageClassOne'>"
        )
        assert log_records[0].levelno == logging.DEBUG
        assert (
            log_records[1].msg
            == "Message failed: $<class 'logger_test.MessageClassOne'>"
        )
        assert log_records[1].levelno == logging.ERROR


def test_middleware_with_custom_log_levels(caplog):
    logger_name = f"{__name__}.{random.randint(1000, 9999)}"
    logger = logging.getLogger(logger_name)

    sut_config = LoggingMiddlewareConfig(
        mgs_received_level=logging.CRITICAL, mgs_succeeded_level=logging.WARNING
    )
    sut = get_logger_middleware(logger, sut_config)
    message_bus = MessageBus(middleswares=[sut])
    message_bus.add_handler(MessageClassOne, get_one)

    message = MessageClassOne()
    with caplog.at_level(logging.DEBUG, logger=logger_name):
        message_bus.handle(message)
        log_records = caplog.records

        assert (
            log_records[0].msg
            == "Message received: $<class 'logger_test.MessageClassOne'>"
        )
        assert log_records[0].levelno == logging.CRITICAL
        assert (
            log_records[1].msg
            == "Message succeeded: $<class 'logger_test.MessageClassOne'>"
        )
        assert log_records[1].levelno == logging.WARNING


def test_middleware_with_custom_log_levels_with_error(caplog):
    logger_name = f"{__name__}.{random.randint(1000, 9999)}"
    logger = logging.getLogger(logger_name)

    sut_config = LoggingMiddlewareConfig(
        mgs_received_level=logging.WARNING, mgs_failed_level=logging.INFO
    )
    sut = get_logger_middleware(logger, sut_config)
    message_bus = MessageBus(middleswares=[sut])
    message_bus.add_handler(MessageClassOne, errorful_handler)

    message = MessageClassOne()
    with caplog.at_level(logging.DEBUG, logger=logger_name):
        with pytest.raises(RuntimeError):
            message_bus.handle(message)
        log_records = caplog.records

        assert (
            log_records[0].msg
            == "Message received: $<class 'logger_test.MessageClassOne'>"
        )
        assert log_records[0].levelno == logging.WARNING
        assert (
            log_records[1].msg
            == "Message failed: $<class 'logger_test.MessageClassOne'>"
        )
        assert log_records[1].levelno == logging.INFO


class MessageClassOne:
    pass


def errorful_handler(message: object) -> object:
    raise RuntimeError("test error")


get_one = lambda _: 1
