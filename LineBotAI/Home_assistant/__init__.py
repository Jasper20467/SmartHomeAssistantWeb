"""
Home Assistant Package

This package provides an API client for interacting with the Smart Home Assistant backend.
"""
from .client import HomeAssistantClient

# Expose all service classes for direct import
from .auth_service import AuthService
from .schedule_service import ScheduleService
from .consumable_service import ConsumableService
from .device_service import DeviceService

# For backward compatibility
HomeAssistantService = HomeAssistantClient
