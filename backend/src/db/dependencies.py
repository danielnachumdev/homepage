from danielutils.abstractions.db import Database  # type: ignore

from .database_factory import DatabaseFactory


def get_db() -> Database:
    return DatabaseFactory.get_database_from_settings()


__all__ = [
    "get_db"
]
