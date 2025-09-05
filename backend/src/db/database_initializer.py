from typing import Sequence, Type

from danielutils.abstractions.db import DatabaseInitializer as BaseDatabaseInitializer
from danielutils.abstractions.db.database_initializer import DeclarativeBase
from .models import SettingsModel, DbSettingsModel
from .population_script import DatabasePopulationScript


class DatabaseInitializer(BaseDatabaseInitializer):
    @classmethod
    def _get_models(cls) -> Sequence[Type[DeclarativeBase]]:
        return [
            SettingsModel,
            DbSettingsModel
        ]

    async def init_db(self, db) -> None:
        """Initialize database and populate with default settings."""
        # Call parent init_db to create tables
        await super().init_db(db)

        # Run population script to populate with default settings
        await DatabasePopulationScript().run_population_if_needed()


__all__ = [
    "DatabaseInitializer"
]
