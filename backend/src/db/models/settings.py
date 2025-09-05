from sqlalchemy import Column, String, Text, DateTime, Index
from typing import Dict, Any
import json

from ...utils.datetime import utc_now
from .base import Base


class SettingsModel(Base):
    """Generic settings database model for storing all application settings."""

    __tablename__ = "settings"

    # Primary key
    id = Column(String, primary_key=True)  # Setting key/identifier

    # Setting metadata
    # e.g., 'chrome_profiles', 'search_engine', 'speedtest'
    category = Column(String, nullable=False)
    # e.g., 'profile_display', 'engine_preference', 'interval'
    setting_type = Column(String, nullable=False)

    # Setting value (stored as JSON)
    # JSON string of the actual setting value
    value = Column(Text, nullable=False)

    # Metadata
    description = Column(String, nullable=True)  # Human-readable description
    # Whether user can edit this setting
    is_user_editable = Column(String, default="true")

    # Timestamps
    created_at = Column(DateTime, default=utc_now())
    updated_at = Column(DateTime, default=utc_now(), onupdate=utc_now())

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_settings_category', 'category'),
        Index('idx_settings_type', 'setting_type'),
        Index('idx_settings_category_type', 'category', 'setting_type'),
    )

    def get_value(self) -> Any:
        """Parse and return the setting value."""
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            return self.value

    def set_value(self, value: Any) -> None:
        """Set the setting value by serializing to JSON."""
        self.value = json.dumps(value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "category": self.category,
            "setting_type": self.setting_type,
            "value": self.get_value(),
            "description": self.description,
            "is_user_editable": self.is_user_editable == "true",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SettingsModel":
        """Create model from dictionary."""
        instance = cls(
            id=data["id"],
            category=data["category"],
            setting_type=data["setting_type"],
            description=data.get("description"),
            is_user_editable=str(data.get("is_user_editable", True)).lower()
        )
        instance.set_value(data["value"])
        return instance

    def __repr__(self) -> str:
        return f"<SettingsModel(id='{self.id}', category='{self.category}', type='{self.setting_type}')>"


__all__ = [
    "SettingsModel"
]
