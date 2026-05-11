"""
Unit tests for LineBotAI/agent/tools.py

Each of the 8 LangChain tools is tested with a mocked HomeAssistantClient to
verify that the correct underlying client method is called with the correct
arguments. External API calls are never made.
"""
import pytest
from unittest.mock import MagicMock, call

from agent.tools import create_tools


# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_ha():
    """Return a fully mocked HomeAssistantClient."""
    client = MagicMock()
    return client


@pytest.fixture
def tools(mock_ha):
    """Return the list of tools bound to the mock client."""
    return create_tools(mock_ha)


def _get_tool(tools_list, name):
    """Find a tool by name from the tools list."""
    return next(t for t in tools_list if t.name == name)


# ---------------------------------------------------------------------------
# Schedule tools
# ---------------------------------------------------------------------------


class TestGetSchedules:
    def test_without_date(self, tools, mock_ha):
        tool = _get_tool(tools, "get_schedules")
        tool.invoke({})
        mock_ha.schedules.get_schedules.assert_called_once_with(date=None)

    def test_with_date(self, tools, mock_ha):
        tool = _get_tool(tools, "get_schedules")
        tool.invoke({"date": "2026-05-11"})
        mock_ha.schedules.get_schedules.assert_called_once_with(date="2026-05-11")

    def test_returns_client_result(self, tools, mock_ha):
        mock_ha.schedules.get_schedules.return_value = [{"id": 1, "title": "Meeting"}]
        tool = _get_tool(tools, "get_schedules")
        result = tool.invoke({})
        assert result == [{"id": 1, "title": "Meeting"}]


class TestCreateSchedule:
    def test_without_description(self, tools, mock_ha):
        tool = _get_tool(tools, "create_schedule")
        tool.invoke({
            "title": "Morning Meeting",
            "start_time": "2026-05-12T09:00:00+08:00",
            "end_time": "2026-05-12T10:00:00+08:00",
        })
        mock_ha.schedules.create_schedule.assert_called_once_with({
            "title": "Morning Meeting",
            "start_time": "2026-05-12T09:00:00+08:00",
            "end_time": "2026-05-12T10:00:00+08:00",
        })

    def test_with_description(self, tools, mock_ha):
        tool = _get_tool(tools, "create_schedule")
        tool.invoke({
            "title": "Lunch",
            "start_time": "2026-05-12T12:00:00+08:00",
            "end_time": "2026-05-12T13:00:00+08:00",
            "description": "Team lunch",
        })
        mock_ha.schedules.create_schedule.assert_called_once_with({
            "title": "Lunch",
            "start_time": "2026-05-12T12:00:00+08:00",
            "end_time": "2026-05-12T13:00:00+08:00",
            "description": "Team lunch",
        })

    def test_returns_client_result(self, tools, mock_ha):
        mock_ha.schedules.create_schedule.return_value = {"id": 42, "title": "Lunch"}
        tool = _get_tool(tools, "create_schedule")
        result = tool.invoke({
            "title": "Lunch",
            "start_time": "2026-05-12T12:00:00+08:00",
            "end_time": "2026-05-12T13:00:00+08:00",
        })
        assert result == {"id": 42, "title": "Lunch"}


class TestUpdateSchedule:
    def test_with_all_fields(self, tools, mock_ha):
        tool = _get_tool(tools, "update_schedule")
        tool.invoke({
            "schedule_id": "7",
            "title": "Updated",
            "start_time": "2026-05-13T08:00:00+08:00",
            "end_time": "2026-05-13T09:00:00+08:00",
            "description": "New notes",
        })
        mock_ha.schedules.update_schedule.assert_called_once_with("7", {
            "title": "Updated",
            "start_time": "2026-05-13T08:00:00+08:00",
            "end_time": "2026-05-13T09:00:00+08:00",
            "description": "New notes",
        })

    def test_with_partial_fields(self, tools, mock_ha):
        tool = _get_tool(tools, "update_schedule")
        tool.invoke({"schedule_id": "3", "title": "Renamed"})
        mock_ha.schedules.update_schedule.assert_called_once_with("3", {"title": "Renamed"})

    def test_with_no_optional_fields(self, tools, mock_ha):
        tool = _get_tool(tools, "update_schedule")
        tool.invoke({"schedule_id": "5"})
        mock_ha.schedules.update_schedule.assert_called_once_with("5", {})


class TestDeleteSchedule:
    def test_calls_correct_method(self, tools, mock_ha):
        tool = _get_tool(tools, "delete_schedule")
        tool.invoke({"schedule_id": "9"})
        mock_ha.schedules.delete_schedule.assert_called_once_with("9")

    def test_returns_client_result(self, tools, mock_ha):
        mock_ha.schedules.delete_schedule.return_value = {"success": True}
        tool = _get_tool(tools, "delete_schedule")
        result = tool.invoke({"schedule_id": "9"})
        assert result == {"success": True}


# ---------------------------------------------------------------------------
# Consumable tools
# ---------------------------------------------------------------------------


class TestGetConsumables:
    def test_calls_correct_method(self, tools, mock_ha):
        tool = _get_tool(tools, "get_consumables")
        tool.invoke({})
        mock_ha.consumables.get_consumables.assert_called_once()

    def test_returns_client_result(self, tools, mock_ha):
        mock_ha.consumables.get_consumables.return_value = [{"id": 1, "name": "Filter"}]
        tool = _get_tool(tools, "get_consumables")
        result = tool.invoke({})
        assert result == [{"id": 1, "name": "Filter"}]


class TestCreateConsumable:
    def test_without_notes(self, tools, mock_ha):
        tool = _get_tool(tools, "create_consumable")
        tool.invoke({
            "name": "Air Filter",
            "category": "filter",
            "installation_date": "2026-05-01",
            "lifetime_days": 90,
        })
        mock_ha.consumables.create_consumable.assert_called_once_with({
            "name": "Air Filter",
            "category": "filter",
            "installation_date": "2026-05-01",
            "lifetime_days": 90,
        })

    def test_with_notes(self, tools, mock_ha):
        tool = _get_tool(tools, "create_consumable")
        tool.invoke({
            "name": "Water Filter",
            "category": "filter",
            "installation_date": "2026-04-01",
            "lifetime_days": 180,
            "notes": "Kitchen sink",
        })
        mock_ha.consumables.create_consumable.assert_called_once_with({
            "name": "Water Filter",
            "category": "filter",
            "installation_date": "2026-04-01",
            "lifetime_days": 180,
            "notes": "Kitchen sink",
        })

    def test_returns_client_result(self, tools, mock_ha):
        mock_ha.consumables.create_consumable.return_value = {"id": 1, "name": "Air Filter"}
        tool = _get_tool(tools, "create_consumable")
        result = tool.invoke({
            "name": "Air Filter",
            "category": "filter",
            "installation_date": "2026-05-01",
            "lifetime_days": 90,
        })
        assert result == {"id": 1, "name": "Air Filter"}


class TestUpdateConsumable:
    def test_with_all_fields(self, tools, mock_ha):
        tool = _get_tool(tools, "update_consumable")
        tool.invoke({
            "consumable_id": "2",
            "name": "HEPA Filter",
            "category": "filter",
            "installation_date": "2026-05-11",
            "lifetime_days": 120,
            "notes": "Updated",
        })
        mock_ha.consumables.update_consumable.assert_called_once_with("2", {
            "name": "HEPA Filter",
            "category": "filter",
            "installation_date": "2026-05-11",
            "lifetime_days": 120,
            "notes": "Updated",
        })

    def test_with_partial_fields(self, tools, mock_ha):
        tool = _get_tool(tools, "update_consumable")
        tool.invoke({"consumable_id": "4", "installation_date": "2026-05-11"})
        mock_ha.consumables.update_consumable.assert_called_once_with(
            "4", {"installation_date": "2026-05-11"}
        )

    def test_with_no_optional_fields(self, tools, mock_ha):
        tool = _get_tool(tools, "update_consumable")
        tool.invoke({"consumable_id": "6"})
        mock_ha.consumables.update_consumable.assert_called_once_with("6", {})


class TestDeleteConsumable:
    def test_calls_correct_method(self, tools, mock_ha):
        tool = _get_tool(tools, "delete_consumable")
        tool.invoke({"consumable_id": "8"})
        mock_ha.consumables.delete_consumable.assert_called_once_with("8")

    def test_returns_client_result(self, tools, mock_ha):
        mock_ha.consumables.delete_consumable.return_value = {"success": True}
        tool = _get_tool(tools, "delete_consumable")
        result = tool.invoke({"consumable_id": "8"})
        assert result == {"success": True}


# ---------------------------------------------------------------------------
# Sanity: correct number of tools returned
# ---------------------------------------------------------------------------


def test_create_tools_returns_eight_tools():
    mock_ha = MagicMock()
    result = create_tools(mock_ha)
    assert len(result) == 8


def test_tool_names(tools):
    names = {t.name for t in tools}
    expected = {
        "get_schedules",
        "create_schedule",
        "update_schedule",
        "delete_schedule",
        "get_consumables",
        "create_consumable",
        "update_consumable",
        "delete_consumable",
    }
    assert names == expected
