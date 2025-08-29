from typing import Sequence, Type

from danielutils import DatabaseInitializer as BaseDatabaseInitializer
from danielutils.abstractions.db.database_initializer import DeclarativeBase
from .models.chrome_profile import ChromeProfileModel


class DatabaseInitializer(BaseDatabaseInitializer):
    @classmethod
    def _get_models(cls) -> Sequence[Type[DeclarativeBase]]:
        return [
            ChromeProfileModel
        ]


__all__ = [
    "DatabaseInitializer"
]
