import typing as t
import logging

# Heavily inspired by the Tactician Logger Middleware :-)
# @link https://github.com/thephpleague/tactician-logger

# pylint: disable=too-few-public-methods


class LoggingMiddlewareConfig(t.NamedTuple):
    mgs_received_level: int = logging.DEBUG
    mgs_succeeded_level: int = logging.DEBUG
    mgs_failed_level: int = logging.ERROR


def get_logger_middleware(
    logger: logging.Logger, config: t.Optional[LoggingMiddlewareConfig] = None
) -> t.Callable:
    # pylint: disable=E1120
    middleware_config: LoggingMiddlewareConfig = config or LoggingMiddlewareConfig()

    def logger_middleware(message: object, next_: t.Callable) -> object:
        message_type = type(message)

        logger.log(
            middleware_config.mgs_received_level, f"Message received: ${message_type}"
        )

        try:
            result = next_(message)
        except Exception as err:
            logger.log(
                middleware_config.mgs_failed_level,
                f"Message failed: ${message_type}",
                exc_info=True,
            )
            raise err

        logger.log(
            middleware_config.mgs_succeeded_level, f"Message succeeded: ${message_type}"
        )

        return result

    return logger_middleware
