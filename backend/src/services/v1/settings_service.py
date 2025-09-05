from typing import Any, Optional
from danielutils.abstractions.db import SelectQuery, UpdateQuery, WhereClause, Condition, Operator

from ...db.dependencies import get_db
from ...schemas.v1.settings import (
    SettingValue, SettingsResponse, SettingUpdateRequest, SettingUpdateResponse,
    BulkSettingsUpdateRequest, BulkSettingsUpdateResponse,
    ChromeProfileSettingValue, ChromeProfileSettingsResponse,
    SearchEngineSettingValue, SearchEngineSettingsResponse,
    SpeedTestSettingValue, SpeedTestSettingsResponse
)
from ...utils.logger import get_logger


class SettingsService:
    """Service for managing application settings."""

    def __init__(self):
        self.logger = get_logger("SettingsService")
        self.db = get_db()

    async def get_all_settings(self) -> SettingsResponse:
        """Get all settings from the database."""
        try:
            query = SelectQuery(table="settings")
            records = await self.db.get(query)

            settings = [SettingValue(**record) for record in records]

            return SettingsResponse(
                success=True,
                settings=settings,
                message=f"Retrieved {len(settings)} settings"
            )
        except Exception as e:
            self.logger.error("Error getting all settings: %s", str(e))
            return SettingsResponse(
                success=False,
                settings=[],
                message=f"Error retrieving settings: {str(e)}"
            )

    async def get_settings_by_category(self, category: str) -> SettingsResponse:
        """Get settings for a specific category."""
        try:
            where_clause = WhereClause(
                conditions=[
                    Condition(column="category",
                              operator=Operator.EQ, value=category)
                ]
            )
            query = SelectQuery(
                table="settings",
                where=where_clause
            )
            records = await self.db.get(query)

            settings = [SettingValue(**record) for record in records]

            return SettingsResponse(
                success=True,
                settings=settings,
                message=f"Retrieved {len(settings)} settings for category '{category}'"
            )
        except Exception as e:
            self.logger.error(
                "Error getting settings for category %s: %s", category, str(e))
            return SettingsResponse(
                success=False,
                settings=[],
                message=f"Error retrieving settings for category '{category}': {str(e)}"
            )

    async def get_setting(self, setting_id: str) -> Optional[SettingValue]:
        """Get a specific setting by ID."""
        try:
            where_clause = WhereClause(
                conditions=[
                    Condition(column="id", operator=Operator.EQ,
                              value=setting_id)
                ]
            )
            query = SelectQuery(
                table="settings",
                where=where_clause
            )
            records = await self.db.get(query)

            if records:
                return SettingValue(**records[0])
            return None
        except Exception as e:
            self.logger.error("Error getting setting %s: %s",
                              setting_id, str(e))
            return None

    async def update_setting(self, request: SettingUpdateRequest) -> SettingUpdateResponse:
        """Update a specific setting."""
        try:
            # Check if setting exists
            existing = await self.get_setting(request.id)
            if not existing:
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
            affected_rows = await self.db.update(query)

            if affected_rows > 0:
                # Get the updated setting
                updated_setting = await self.get_setting(request.id)
                return SettingUpdateResponse(
                    success=True,
                    message=f"Setting '{request.id}' updated successfully",
                    setting=updated_setting
                )
            else:
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
        try:
            # Check if setting exists
            existing = await self.get_setting(setting_id)

            if existing:
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
                affected_rows = await self.db.update(query)

                if affected_rows > 0:
                    updated_setting = await self.get_setting(setting_id)
                    return SettingUpdateResponse(
                        success=True,
                        message=f"Setting '{setting_id}' updated successfully",
                        setting=updated_setting
                    )
                else:
                    return SettingUpdateResponse(
                        success=False,
                        message=f"Failed to update setting '{setting_id}'"
                    )
            else:
                # Create new setting
                data = {
                    "id": setting_id,
                    "category": category,
                    "setting_type": setting_type,
                    "value": value,
                    "description": description,
                    "is_user_editable": str(is_user_editable).lower()
                }

                await self.db.insert("settings", data)

                # Get the created setting
                created_setting = await self.get_setting(setting_id)
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
        updated_settings = []
        failed_updates = []

        try:
            for setting_request in request.settings:
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
                        else:
                            failed_updates.append({
                                "id": setting_request.id,
                                "error": "Failed to update setting"
                            })
                    else:
                        failed_updates.append({
                            "id": setting_request.id,
                            "error": "Setting not found"
                        })
                except Exception as e:
                    failed_updates.append({
                        "id": setting_request.id,
                        "error": str(e)
                    })

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

    async def get_chrome_profile_settings(self) -> ChromeProfileSettingsResponse:
        """Get Chrome profile settings."""
        try:
            response = await self.get_settings_by_category("chrome_profiles")
            if not response.success:
                return ChromeProfileSettingsResponse(
                    success=False,
                    profiles=[],
                    message=response.message
                )

            profiles = []
            for setting in response.settings:
                if setting.setting_type == "profile_display":
                    value = setting.value
                    if isinstance(value, dict):
                        profiles.append(ChromeProfileSettingValue(**value))

            return ChromeProfileSettingsResponse(
                success=True,
                profiles=profiles,
                message=f"Retrieved {len(profiles)} Chrome profile settings"
            )
        except Exception as e:
            self.logger.error(
                "Error getting Chrome profile settings: %s", str(e))
            return ChromeProfileSettingsResponse(
                success=False,
                profiles=[],
                message=f"Error retrieving Chrome profile settings: {str(e)}"
            )

    async def update_chrome_profile_setting(
        self,
        profile_id: str,
        display_name: str,
        icon: str,
        enabled: bool
    ) -> SettingUpdateResponse:
        """Update Chrome profile setting."""
        setting_id = f"chrome_profile_{profile_id}"
        value = {
            "profile_id": profile_id,
            "display_name": display_name,
            "icon": icon,
            "enabled": enabled
        }

        return await self.create_or_update_setting(
            setting_id=setting_id,
            category="chrome_profiles",
            setting_type="profile_display",
            value=value,
            description=f"Display settings for Chrome profile {profile_id}",
            is_user_editable=True
        )

    async def get_search_engine_setting(self) -> SearchEngineSettingsResponse:
        """Get search engine setting."""
        try:
            setting = await self.get_setting("search_engine_preference")
            if not setting:
                # Return default if not found
                default_setting = SearchEngineSettingValue(
                    selected_engine="google")
                return SearchEngineSettingsResponse(
                    success=True,
                    setting=default_setting,
                    message="Using default search engine setting"
                )

            value = setting.value
            if isinstance(value, dict):
                search_engine_setting = SearchEngineSettingValue(**value)
            else:
                search_engine_setting = SearchEngineSettingValue(
                    selected_engine=str(value))

            return SearchEngineSettingsResponse(
                success=True,
                setting=search_engine_setting,
                message="Retrieved search engine setting"
            )
        except Exception as e:
            self.logger.error(
                "Error getting search engine setting: %s", str(e))
            return SearchEngineSettingsResponse(
                success=False,
                setting=SearchEngineSettingValue(selected_engine="google"),
                message=f"Error retrieving search engine setting: {str(e)}"
            )

    async def update_search_engine_setting(self, selected_engine: str) -> SettingUpdateResponse:
        """Update search engine setting."""
        value = {
            "selected_engine": selected_engine
        }

        return await self.create_or_update_setting(
            setting_id="search_engine_preference",
            category="search_engine",
            setting_type="engine_preference",
            value=value,
            description="User's preferred search engine",
            is_user_editable=True
        )

    async def get_speed_test_setting(self) -> SpeedTestSettingsResponse:
        """Get speed test setting."""
        try:
            setting = await self.get_setting("speed_test_enabled")
            if not setting:
                # Return default if not found (disabled by default)
                default_setting = SpeedTestSettingValue(enabled=False)
                return SpeedTestSettingsResponse(
                    success=True,
                    setting=default_setting,
                    message="Using default speed test setting"
                )

            value = setting.value
            if isinstance(value, dict):
                speed_test_setting = SpeedTestSettingValue(**value)
            else:
                speed_test_setting = SpeedTestSettingValue(enabled=bool(value))

            return SpeedTestSettingsResponse(
                success=True,
                setting=speed_test_setting,
                message="Retrieved speed test setting"
            )
        except Exception as e:
            self.logger.error("Error getting speed test setting: %s", str(e))
            return SpeedTestSettingsResponse(
                success=False,
                setting=SpeedTestSettingValue(enabled=False),
                message=f"Error retrieving speed test setting: {str(e)}"
            )

    async def update_speed_test_setting(self, enabled: bool) -> SettingUpdateResponse:
        """Update speed test setting."""
        value = {
            "enabled": enabled
        }

        return await self.create_or_update_setting(
            setting_id="speed_test_enabled",
            category="widgets",
            setting_type="enabled",
            value=value,
            description="Enable or disable internet speed test widget",
            is_user_editable=True
        )


__all__ = [
    "SettingsService"
]
