"""Rich logging setup for mzero."""

import logging
from rich.logging import RichHandler
from rich.console import Console

console = Console()

def get_logger(name: str = "mzero") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = RichHandler(console=console, rich_tracebacks=True, show_time=True, show_path=False)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    return logger

logger = get_logger("mzero")
