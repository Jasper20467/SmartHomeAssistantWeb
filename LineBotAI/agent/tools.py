"""
LangGraph Agent Tools

Defines LangChain @tool-decorated functions wrapping HomeAssistantClient methods.
Each tool is designed for LLM-driven reasoning and action execution.
"""
from typing import Any, Dict, Optional
from langchain_core.tools import tool

from Home_assistant.client import HomeAssistantClient


def create_tools(ha_client: HomeAssistantClient) -> list:
    """
    Build and return all 8 agent tools bound to the given HomeAssistantClient instance.

    Args:
        ha_client: Initialized HomeAssistantClient connected to the backend API.

    Returns:
        List of LangChain tool callables.
    """

    @tool
    def get_schedules(date: Optional[str] = None) -> Any:
        """
        Retrieve a list of schedules from the backend.

        Use this tool when the user asks to view, check, or list schedules or appointments.

        Args:
            date: Optional date filter in YYYY-MM-DD format (Taiwan time, UTC+8).
                  When provided, returns only schedules for that specific date.
                  When omitted, returns all schedules.

        Returns:
            A list of schedule objects. Each object contains fields such as
            id, title, start_time, end_time, and description.
        """
        return ha_client.schedules.get_schedules(date=date)

    @tool
    def create_schedule(
        title: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
    ) -> Any:
        """
        Create a new schedule in the backend.

        Use this tool when the user wants to add, create, or set up a new schedule
        or appointment.

        Args:
            title: Short name or title of the schedule (e.g., "Morning Meeting").
            start_time: Start time in ISO 8601 format including timezone offset,
                        e.g. "2026-05-12T09:00:00+08:00". Always use UTC+8 (Taiwan time).
            end_time: End time in ISO 8601 format including timezone offset,
                      e.g. "2026-05-12T10:00:00+08:00".
            description: Optional longer description or notes for the schedule.

        Returns:
            The created schedule object with its assigned id.
        """
        data: Dict[str, Any] = {
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
        }
        if description is not None:
            data["description"] = description
        return ha_client.schedules.create_schedule(data)

    @tool
    def update_schedule(
        schedule_id: str,
        title: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Any:
        """
        Update an existing schedule in the backend.

        Use this tool when the user wants to modify, change, or edit a schedule.
        Only provide fields that need to be updated; omit unchanged fields.

        Args:
            schedule_id: The unique identifier of the schedule to update.
            title: New title for the schedule (optional).
            start_time: New start time in ISO 8601 format with UTC+8 offset (optional).
            end_time: New end time in ISO 8601 format with UTC+8 offset (optional).
            description: New description or notes (optional).

        Returns:
            The updated schedule object.
        """
        data: Dict[str, Any] = {}
        if title is not None:
            data["title"] = title
        if start_time is not None:
            data["start_time"] = start_time
        if end_time is not None:
            data["end_time"] = end_time
        if description is not None:
            data["description"] = description
        return ha_client.schedules.update_schedule(schedule_id, data)

    @tool
    def delete_schedule(schedule_id: str) -> Any:
        """
        Delete a schedule from the backend.

        Use this tool when the user wants to remove, cancel, or delete a schedule
        or appointment.

        Args:
            schedule_id: The unique identifier of the schedule to delete.

        Returns:
            A confirmation dict indicating success or failure.
        """
        return ha_client.schedules.delete_schedule(schedule_id)

    @tool
    def get_consumables() -> Any:
        """
        Retrieve a list of all consumable items tracked in the home.

        Use this tool when the user asks to view, check, or list consumables,
        household supplies, or items with remaining usage days.

        Returns:
            A list of consumable objects. Each object contains fields such as
            id, name, category, installation_date, lifetime_days, notes, and days_remaining.
        """
        return ha_client.consumables.get_consumables()

    @tool
    def create_consumable(
        name: str,
        category: str,
        installation_date: str,
        lifetime_days: int,
        notes: Optional[str] = None,
    ) -> Any:
        """
        Create a new consumable item in the backend.

        Use this tool when the user wants to add or register a new household consumable,
        such as a filter, battery, or household product.

        Args:
            name: Name of the consumable item (e.g., "Air Filter", "Water Filter").
            category: Category of the item (e.g., "filter", "battery", "cleaning").
            installation_date: Date the item was installed or started, in YYYY-MM-DD format.
            lifetime_days: Expected lifespan of the item in days (e.g., 90 for 3 months).
            notes: Optional additional notes for the item.

        Returns:
            The created consumable object with its assigned id.
        """
        data: Dict[str, Any] = {
            "name": name,
            "category": category,
            "installation_date": installation_date,
            "lifetime_days": lifetime_days,
        }
        if notes is not None:
            data["notes"] = notes
        return ha_client.consumables.create_consumable(data)

    @tool
    def update_consumable(
        consumable_id: str,
        name: Optional[str] = None,
        category: Optional[str] = None,
        installation_date: Optional[str] = None,
        lifetime_days: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Any:
        """
        Update an existing consumable item in the backend.

        Use this tool when the user wants to modify or edit a consumable's information,
        such as updating the installation date after replacing a filter.
        Only provide fields that need to be updated; omit unchanged fields.

        Args:
            consumable_id: The unique identifier of the consumable to update.
            name: New name for the consumable (optional).
            category: New category for the consumable (optional).
            installation_date: New installation or replacement date in YYYY-MM-DD format (optional).
            lifetime_days: New expected lifespan in days (optional).
            notes: New notes for the consumable (optional).

        Returns:
            The updated consumable object.
        """
        data: Dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if category is not None:
            data["category"] = category
        if installation_date is not None:
            data["installation_date"] = installation_date
        if lifetime_days is not None:
            data["lifetime_days"] = lifetime_days
        if notes is not None:
            data["notes"] = notes
        return ha_client.consumables.update_consumable(consumable_id, data)

    @tool
    def delete_consumable(consumable_id: str) -> Any:
        """
        Delete a consumable item from the backend.

        Use this tool when the user wants to remove or delete a consumable item
        from the tracking list.

        Args:
            consumable_id: The unique identifier of the consumable to delete.

        Returns:
            A confirmation dict indicating success or failure.
        """
        return ha_client.consumables.delete_consumable(consumable_id)

    return [
        get_schedules,
        create_schedule,
        update_schedule,
        delete_schedule,
        get_consumables,
        create_consumable,
        update_consumable,
        delete_consumable,
    ]
