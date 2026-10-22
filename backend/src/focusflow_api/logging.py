import logging
import sys

import structlog
from structlog.contextvars import merge_contextvars
from structlog.processors import (
    JSONRenderer,
    TimeStamper,
    add_log_level,
    format_exc_info,
)
from structlog.stdlib import ProcessorFormatter


def _configure_uvicorn_logging():
    for name in ["uvicorn", "uvicorn.access"]:
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True


def configure_logging():

    shared_processors = [
        merge_contextvars,
        add_log_level,
        TimeStamper(fmt="iso"),
        format_exc_info,
    ]

    processor_formatter = ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[ProcessorFormatter.remove_processors_meta, JSONRenderer()],
    )

    structlog.configure(
        processors=[*shared_processors, processor_formatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(processor_formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [stream_handler]
    root_logger.setLevel(logging.INFO)

    _configure_uvicorn_logging()
