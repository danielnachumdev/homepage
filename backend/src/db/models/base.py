from sqlalchemy.orm import DeclarativeBase
from typing import Dict, Any


class Base(DeclarativeBase):
    def dict(self) -> Dict[str, Any]:
        """Convert the model instance to a dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
