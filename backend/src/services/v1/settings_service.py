from typing import Any, Optional
from danielutils.abstractions.db import SelectQuery, UpdateQuery, WhereClause, Condition, Operator

from ...db.dependencies import get_db
from ...schemas.v1.settings import (
    SettingValue, SettingsResponse, SettingUpdateRequest, SettingUpdateResponse,
    BulkSettingsUpdateRequest, BulkSettingsUpdateResponse
)
from ...utils.logger import get_logger


class SettingsService:
    """Service for managing application settings."""

    def __init__(self):
        self.logger = get_logger("SettingsService")
        self.db = get_db()

    async def get_all_settings(self) -> SettingsResponse:
        """Get all settings from the database in a generic format."""
        self.logger.info("Starting to retrieve all settings from database")
        try:
            query = SelectQuery(table="settings")
            self.logger.debug("Executing database query to fetch all settings")
            records = await self.db.get(query)

            settings = [SettingValue(**record) for record in records]
            self.logger.info("Successfully retrieved %d settings from database", len(settings))

            return SettingsResponse(
                success=True,
                message=f"Retrieved {len(settings)} settings",
                settings=settings
            )
        except Exception as e:
            self.logger.error("Error getting all settings: %s", str(e))
            return SettingsResponse(
                success=False,
                message=f"Error retrieving settings: {str(e)}",
                settings=[]
            )

    async def get_setting(self, setting_id: str) -> Optional[SettingValue]:
        """Get a specific setting by ID."""
        self.logger.info("Starting to retrieve setting with ID: %s", setting_id)
        try:
            where_clause = WhereClause(
                conditions=[
                    Condition(column="id", operator=Operator.EQ,
                              value=setting_id)
                ]
            )
            query = SelectQuery(table="settings", where=where_clause)
            self.logger.debug("Executing database query to fetch setting: %s", setting_id)
            records = await self.db.get(query)

            if records:
                self.logger.info("Successfully retrieved setting: %s", setting_id)
                return SettingValue(**records[0])
            else:
                self.logger.warning("Setting not found: %s", setting_id)
                return None
        except Exception as e:
            self.logger.error("Error getting setting %s: %s",
                              setting_id, str(e))
            return None

    async def update_setting(self, request: SettingUpdateRequest) -> SettingUpdateResponse:
        """Update a specific setting."""
        self.logger.info("Starting to update setting: %s with value: %s", request.id, request.value)
        try:
            # Check if setting exists
            self.logger.debug("Checking if setting exists: %s", request.id)
            existing = await self.get_setting(request.id)
            if not existing:
                self.logger.warning("Setting not found for update: %s", request.id)
                return SettingUpdateResponse(
                    success=False,
                    message=f"Setting '{request.id}' not found"
                )

            # Update the setting
            where_clause = WhereClause(
                conditions=[
                    Condition(column="id", operator=Operator.EQ,
                              value=request.id)
                ]
            )
            query = UpdateQuery(
                table="settings",
                where=where_clause,
                data={"value": request.value}
            )
            self.logger.debug("Executing database update for setting: %s", request.id)
            affected_rows = await self.db.update(query)

            if affected_rows > 0:
                self.logger.info("Successfully updated setting: %s", request.id)
                # Get the updated setting
                updated_setting = await self.get_setting(request.id)
                return SettingUpdateResponse(
                    success=True,
                    message=f"Setting '{request.id}' updated successfully",
                    setting=updated_setting
                )
            else:
                self.logger.warning("No rows affected when updating setting: %s", request.id)
                return SettingUpdateResponse(
                    success=False,
                    message=f"Setting '{request.id}' not found"
                )
        except Exception as e:
            self.logger.error("Error updating setting %s: %s",
                              request.id, str(e))
            return SettingUpdateResponse(
                success=False,
                message=f"Error updating setting '{request.id}': {str(e)}"
            )

    async def create_or_update_setting(
        self,
        setting_id: str,
        category: str,
        setting_type: str,
        value: Any,
        description: Optional[str] = None,
        is_user_editable: bool = True
    ) -> SettingUpdateResponse:
        """Create or update a setting."""
        self.logger.info("Starting create_or_update_setting for ID: %s, category: %s, type: %s",
                         setting_id, category, setting_type)
        try:
            # Check if setting exists
            self.logger.debug("Checking if setting exists: %s", setting_id)
            existing = await self.get_setting(setting_id)

            if existing:
                self.logger.info("Setting exists, updating: %s", setting_id)
                # Update existing setting
                where_clause = WhereClause(
                    conditions=[
                        Condition(column="id", operator=Operator.EQ,
                                  value=setting_id)
                    ]
                )
                query = UpdateQuery(
                    table="settings",
                    where=where_clause,
                    data={
                        "value": value,
                        "description": description,
                        "is_user_editable": str(is_user_editable).lower()
                    }
                )
                self.logger.debug("Executing database update for existing setting: %s", setting_id)
                affected_rows = await self.db.update(query)

                if affected_rows > 0:
                    self.logger.info("Successfully updated existing setting: %s", setting_id)
                    updated_setting = await self.get_setting(setting_id)
                    return SettingUpdateResponse(
                        success=True,
                        message=f"Setting '{setting_id}' updated successfully",
                        setting=updated_setting
                    )
                else:
                    self.logger.warning("No rows affected when updating existing setting: %s", setting_id)
                    return SettingUpdateResponse(
                        success=False,
                        message=f"Failed to update setting '{setting_id}'"
                    )
            else:
                self.logger.info("Setting does not exist, creating new: %s", setting_id)
                # Create new setting
                data = {
                    "id": setting_id,
                    "category": category,
                    "setting_type": setting_type,
                    "value": value,
                    "description": description,
                    "is_user_editable": str(is_user_editable).lower()
                }

                self.logger.debug("Executing database insert for new setting: %s", setting_id)
                await self.db.insert("settings", data)

                # Get the created setting
                created_setting = await self.get_setting(setting_id)
                self.logger.info("Successfully created new setting: %s", setting_id)
                return SettingUpdateResponse(
                    success=True,
                    message=f"Setting '{setting_id}' created successfully",
                    setting=created_setting
                )
        except Exception as e:
            self.logger.error(
                "Error creating/updating setting %s: %s", setting_id, str(e))
            return SettingUpdateResponse(
                success=False,
                message=f"Error creating/updating setting '{setting_id}': {str(e)}"
            )

    async def bulk_update_settings(self, request: BulkSettingsUpdateRequest) -> BulkSettingsUpdateResponse:
        """Update multiple settings at once."""
        self.logger.info("Starting bulk update for %d settings", len(request.settings))
        updated_settings = []
        failed_updates = []

        try:
            for i, setting_request in enumerate(request.settings):
                self.logger.debug("Processing setting %d/%d: %s", i + 1, len(request.settings), setting_request.id)
                try:
                    # Check if setting exists
                    existing = await self.get_setting(setting_request.id)

                    if existing:
                        # Update the setting
                        where_clause = WhereClause(
                            conditions=[
                                Condition(
                                    column="id", operator=Operator.EQ, value=setting_request.id)
                            ]
                        )
                        query = UpdateQuery(
                            table="settings",
                            where=where_clause,
                            data={"value": setting_request.value}
                        )
                        affected_rows = await self.db.update(query)

                        if affected_rows > 0:
                            updated_setting = await self.get_setting(setting_request.id)
                            updated_settings.append(updated_setting)
                            self.logger.debug("Successfully updated setting in bulk: %s", setting_request.id)
                        else:
                            failed_updates.append({
                                "id": setting_request.id,
                                "error": "Failed to update setting"
                            })
                            self.logger.warning(
                                "Failed to update setting in bulk (no rows affected): %s",
                                setting_request.id)
                    else:
                        failed_updates.append({
                            "id": setting_request.id,
                            "error": "Setting not found"
                        })
                        self.logger.warning("Setting not found in bulk update: %s", setting_request.id)
                except Exception as e:
                    failed_updates.append({
                        "id": setting_request.id,
                        "error": str(e)
                    })
                    self.logger.error("Error updating setting in bulk %s: %s", setting_request.id, str(e))

            success_count = len(updated_settings)
            failure_count = len(failed_updates)
            self.logger.info("Bulk update completed: %d successful, %d failed", success_count, failure_count)

            return BulkSettingsUpdateResponse(
                success=len(failed_updates) == 0,
                updated_settings=updated_settings,
                failed_updates=failed_updates,
                message=f"Updated {len(updated_settings)} settings, {len(failed_updates)} failed"
            )
        except Exception as e:
            self.logger.error("Error in bulk update: %s", str(e))
            return BulkSettingsUpdateResponse(
                success=False,
                updated_settings=[],
                failed_updates=[{"error": str(e)}],
                message=f"Error in bulk update: {str(e)}"
            )

    # Convenience methods for specific setting types
    async def update_speed_test_setting(self, enabled: bool) -> SettingUpdateResponse:
        """Update speed test setting."""
        self.logger.info("Updating speed test setting: enabled=%s", enabled)
        value = {"enabled": enabled}
        result = await self.create_or_update_setting(
            setting_id="speed_test_enabled",
            category="widgets",
            setting_type="enabled",
            value=value,
            description="Enable or disable internet speed test widget",
            is_user_editable=True
        )
        if result.success:
            self.logger.info("Successfully updated speed test setting")
        else:
            self.logger.error("Failed to update speed test setting: %s", result.message)
        return result

    async def update_search_engine_setting(self, selected_engine: str) -> SettingUpdateResponse:
        """Update search engine setting."""
        self.logger.info("Updating search engine setting: %s", selected_engine)
        value = {"selected_engine": selected_engine}
        result = await self.create_or_update_setting(
            setting_id="search_engine_preference",
            category="search_engine",
            setting_type="engine_preference",
            value=value,
            description="User's preferred search engine",
            is_user_editable=True
        )
        if result.success:
            self.logger.info("Successfully updated search engine setting")
        else:
            self.logger.error("Failed to update search engine setting: %s", result.message)
        return result

    async def update_chrome_profile_setting(
        self,
        profile_id: str,
        display_name: str,
        icon: str,
        enabled: bool
    ) -> SettingUpdateResponse:
        """Update Chrome profile setting."""
        self.logger.info("Updating Chrome profile setting: %s, display_name=%s, enabled=%s",
                         profile_id, display_name, enabled)
        setting_id = f"chrome_profile_{profile_id}"
        value = {
            "profile_id": profile_id,
            "display_name": display_name,
            "icon": icon,
            "enabled": enabled
        }
        result = await self.create_or_update_setting(
            setting_id=setting_id,
            category="chrome_profiles",
            setting_type="profile_display",
            value=value,
            description=f"Display settings for Chrome profile {profile_id}",
            is_user_editable=True
        )
        if result.success:
            self.logger.info("Successfully updated Chrome profile setting: %s", profile_id)
        else:
            self.logger.error("Failed to update Chrome profile setting %s: %s", profile_id, result.message)
        return result


__all__ = [
    "SettingsService"
]
