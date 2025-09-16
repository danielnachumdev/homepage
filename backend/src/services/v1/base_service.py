import logging

from ...utils.logger import get_logger


class BaseService:
    logger: logging.Logger

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        cls.logger = get_logger(cls.__module__)


__all__ = [
    "BaseService"
]
