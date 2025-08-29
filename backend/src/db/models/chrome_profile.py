from sqlalchemy import Column, String, Boolean, DateTime

from ...utils.datetime import utc_now

from .base import Base


class ChromeProfileModel(Base):
    """Chrome profile database model."""

    __tablename__ = "chrome_profiles"

    # Primary key and basic info
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    icon = Column(String, nullable=True)

    # Profile state
    is_active = Column(Boolean, default=False)
    is_visible = Column(Boolean, default=True)

    # System path
    path = Column(String, nullable=True)

    # Extracted profile information
    profile_name = Column(String, nullable=True)
    account_id = Column(String, nullable=True)
    email = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    given_name = Column(String, nullable=True)
    picture_url = Column(String, nullable=True)
    locale = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=utc_now())
    updated_at = Column(DateTime, default=utc_now(), onupdate=utc_now())

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "icon": self.icon,
            "is_active": self.is_active,
            "is_visible": self.is_visible,
            "path": self.path,
            "profile_name": self.profile_name,
            "account_id": self.account_id,
            "email": self.email,
            "full_name": self.full_name,
            "given_name": self.given_name,
            "picture_url": self.picture_url,
            "locale": self.locale,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChromeProfileModel":
        """Create model from dictionary."""
        return cls(**data)


__all__ = [
    "ChromeProfileModel"
]
