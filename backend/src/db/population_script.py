"""
Database population script to initialize default settings based on frontend defaults.
This script populates the database with default values that match the frontend DEFAULT_SETTINGS.
"""

import json
from typing import Dict, Any, List
from danielutils.abstractions.db import SelectQuery, UpdateQuery, WhereClause, Condition, Operator

from .dependencies import get_db
from ..utils.logger import get_logger


class DatabasePopulationScript:
    """Script to populate the database with default settings."""

    def __init__(self):
        self.logger = get_logger("DatabasePopulationScript")
        self.db = get_db()

    async def _is_database_populated(self) -> bool:
        """Check if the database has already been populated with default settings."""
        try:
            query = SelectQuery(table="db_settings")
            records = await self.db.get(query)

            if not records:
                return False

            # Check if the main record exists and is populated
            main_record: Dict = next(
                (record for record in records if record.get("id") == "main"), None)
            return main_record.get("is_populated", False) if main_record else False

        except (KeyError, ValueError, TypeError) as e:
            self.logger.warning("Error checking population status: %s", str(e))
            return False

    async def _mark_database_as_populated(self) -> None:
        """Mark the database as populated in the db_settings table."""
        try:
            # Check if db_settings record exists
            query = SelectQuery(table="db_settings")
            records = await self.db.get(query)

            if not records:
                # Create new record
                await self.db.insert("db_settings", {
                    "id": "main",
                    "is_populated": True,
                    "db_version": "1.0.0"
                })
            else:
                # Update existing record
                update_query = UpdateQuery(
                    table="db_settings",
                    data={"is_populated": True},
                    where_clause=WhereClause(
                        conditions=[
                            Condition(column="id", operator=Operator.EQ, value="main")]
                    )
                )
                await self.db.update(update_query)

            self.logger.info("Database marked as populated")

        except (KeyError, ValueError, TypeError) as e:
            self.logger.error(
                "Error marking database as populated: %s", str(e))
            raise

    def _get_default_settings(self) -> List[Dict[str, Any]]:
        """
        Get default settings based on frontend DEFAULT_SETTINGS.
        Returns a list of settings to be inserted into the database.
        """
        return [
            # Speed Test Widget Settings
            {
                "id": "speedtest_enabled",
                "category": "widgets",
                "setting_type": "speedtest",
                "value": json.dumps({"enabled": False}),
                "description": "Enable/disable the speed test widget",
                "is_user_editable": "true"
            },

            # Search Engine Settings
            {
                "id": "search_engine_selected",
                "category": "search_engine",
                "setting_type": "selected_engine",
                "value": json.dumps({"selected_engine": "google"}),
                "description": "Selected search engine for the homepage",
                "is_user_editable": "true"
            }
        ]

    async def _get_chrome_profiles_settings(self) -> List[Dict[str, Any]]:
        """
        Get Chrome profiles settings by detecting available Chrome profiles.
        Returns a list of Chrome profile settings to be inserted into the database.
        """
        try:
            self.logger.info("Detecting Chrome profiles...")

            # Import ChromeService locally to avoid circular imports
            from ..services.v1.chrome_service import ChromeService
            profiles_response = await ChromeService().discover()

            if not profiles_response.success:
                self.logger.warning(
                    "Failed to detect Chrome profiles: %s", profiles_response.message)
                return []

            chrome_settings = []
            for profile in profiles_response.profiles:
                # Convert profile ID to snake_case for database storage
                profile_id_snake = profile.id.replace(" ", "_").replace("-", "_").lower()
                setting_data = {
                    "id": f"chrome_profile_{profile_id_snake}",
                    "category": "chrome_profiles",
                    "setting_type": "profile_display",
                    "value": json.dumps({
                        "profile_id": profile.id,  # Keep original ID in the value
                        "display_name": profile.name,
                        "icon": profile.icon or "👤",
                        "enabled": profile.is_visible or True
                    }),
                    "description": f"Display settings for Chrome profile {profile.name}",
                    "is_user_editable": "true"
                }
                chrome_settings.append(setting_data)

            return chrome_settings

        except (ImportError, AttributeError, TypeError, ValueError) as e:
            self.logger.error("Error detecting Chrome profiles: %s", str(e))
            return []

    async def _populate_default_settings(self) -> None:
        """Populate the database with default settings."""
        try:
            self.logger.info(
                "Starting database population with default settings...")

            # Check if already populated
            if await self._is_database_populated():
                self.logger.info(
                    "Database already populated, skipping population script")
                return

            # Get default settings
            default_settings: List[Dict] = self._get_default_settings()

            # Get Chrome profiles settings
            chrome_profiles_settings: List[Dict] = await self._get_chrome_profiles_settings()

            # Combine all settings
            all_settings = default_settings + chrome_profiles_settings

            # Insert each setting
            for setting_data in all_settings:
                try:
                    # Check if setting already exists
                    query = SelectQuery(
                        table="settings",
                        where=WhereClause(
                            conditions=[
                                Condition(column="id", operator=Operator.EQ, value=setting_data["id"])]
                        )
                    )
                    existing_records = await self.db.get(query)

                    if existing_records:
                        self.logger.info(
                            "Setting %s already exists, skipping", setting_data["id"])
                        continue

                    # Insert new setting
                    await self.db.insert("settings", setting_data)
                    self.logger.info(
                        "Inserted default setting: %s", setting_data["id"])

                except (KeyError, ValueError, TypeError) as e:
                    self.logger.error(
                        "Error inserting setting %s: %s", setting_data["id"], str(e))
                    # Continue with other settings even if one fails
                    continue

            # Mark database as populated
            await self._mark_database_as_populated()

            self.logger.info("Database population completed successfully")

        except (KeyError, ValueError, TypeError) as e:
            self.logger.error("Error during database population: %s", str(e))
            raise

    async def run_population_if_needed(self) -> None:
        """Run population script only if the database hasn't been populated yet."""
        try:
            if not await self._is_database_populated():
                await self._populate_default_settings()
            else:
                self.logger.info(
                    "Database already populated, skipping population script")
        except (KeyError, ValueError, TypeError) as e:
            self.logger.error("Error running population script: %s", str(e))
            raise


__all__ = [
    "DatabasePopulationScript"
]
