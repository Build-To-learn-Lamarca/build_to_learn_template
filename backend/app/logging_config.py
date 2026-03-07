"""Logging configuration — structlog with JSON in production, console in dev."""

from __future__ import annotations

import logging
import sys

import structlog


def configure_logging(
    log_level: str = "INFO",
    json_logs: bool | None = None,
    debug: bool = False,
) -> None:
    """Configure structlog for app code using structlog.get_logger().

    When json_logs is True (default when not debug), use JSON renderer for
    observability (aggregators, ELK, etc.). Otherwise use console-friendly output.
    """
    if json_logs is None:
        json_logs = not debug

    shared_processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if json_logs:
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty()),
        ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )
