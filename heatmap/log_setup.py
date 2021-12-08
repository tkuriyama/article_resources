"""Helper for setting up module-specific logging.
"""

import logging # type: ignore
from logging import StreamHandler # type: ignore
from typing import Optional # type: ignore


################################################################################


def init_stream_log(fname: str,
                    level: int = logging.INFO,
                    fmt: Optional[logging.Formatter] = None,
                    ) -> logging.Logger:
    """Initialize and return a stream logger."""
    logger = logging.getLogger(fname)
    logger.setLevel(level)

    sh = StreamHandler()
    default_fmt = logging.Formatter(
        '%(asctime)s - %(levelname)s - {} - %(message)s'.format(fname))
    sh.setFormatter(default_fmt if fmt is None else fmt)
    logger.addHandler(sh)

    return logger


def init_notebook_log(level: int = logging.INFO,
                      fmt: Optional[logging.Formatter] = None,
                    ) -> logging.Logger:
    """Initialize and return a logger for use in Jupyter Notebook.
    Try to use the default Jupyter Notebook StdErr handler.
    """
    logger = logging.getLogger('Notebook')

    fmt_s = '%(asctime)s - %(levelname)s - Notebook - %(message)s'
    default_fmt = logging.Formatter(fmt_s)

    if len(logger.handlers) >= 1:
        logger.handlers = logger.handlers[:1]
        h = logger.handlers[0]
    else:
        h = StreamHandler()
        logger.addHandler(h)

    h.setFormatter(default_fmt if fmt is None else fmt)
    logger.setLevel(level)
    logger.propagate = False

    return logger
