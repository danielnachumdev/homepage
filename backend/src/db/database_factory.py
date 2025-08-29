from danielutils import DatabaseFactory as BaseDatabaseFactory, Database


class DatabaseFactory(BaseDatabaseFactory):
    @classmethod
    def get_database_from_settings(cls) -> Database:
        return cls.get_database(db_type="persistent_memory",db_kwargs=dict(data_dir="./"))


__all__ = [
    "DatabaseFactory"
]
