from sqlalchemy import Column, Boolean, DateTime, String
from typing import Dict, Any

from ...utils.datetime import utc_now
from .base import Base


class DbSettingsModel(Base):
    """Database settings model to track database initialization and population status."""

    __tablename__ = "db_settings"

    # Primary key - only one record should exist
    id = Column(String, primary_key=True, default="main")

    # Population status
    is_populated = Column(Boolean, default=False, nullable=False)

    # Database version for future migrations
    db_version = Column(String, default="1.0.0", nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=utc_now())
    updated_at = Column(DateTime, default=utc_now(), onupdate=utc_now())

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "is_populated": self.is_populated,
            "db_version": self.db_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        return f"<DbSettingsModel(id='{self.id}', is_populated={self.is_populated}, version='{self.db_version}')>"


__all__ = [
    "DbSettingsModel"
]
