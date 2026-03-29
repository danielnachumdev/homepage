from typing import Any, Dict

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def dict(self) -> Dict[str, Any]:
        """Convert the model instance to a dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
