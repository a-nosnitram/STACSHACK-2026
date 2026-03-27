import logging
from typing import Optional


def setup_logging(level: str = "INFO", fmt: Optional[str] = None) -> None:
    if fmt is None:
        fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format=fmt)
