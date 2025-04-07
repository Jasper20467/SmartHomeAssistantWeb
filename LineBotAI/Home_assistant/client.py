"""
Home Assistant Client

Main client class that integrates all service modules.
"""
import logging
from typing import Optional

from .base_service import BaseService
from .auth_service import AuthService
from .schedule_service import ScheduleService
from .consumable_service import ConsumableService
from .device_service import DeviceService
from .room_service import RoomService
from .scene_service import SceneService
from .automation_service import AutomationService
from .state_service import StateService


class HomeAssistantClient:
    """Client for interacting with Smart Home Assistant backend API."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """Initialize the Home Assistant Client with backend API URL and optional API key."""
        self.base_url = base_url.rstrip('/')  # Remove trailing slash if present
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        self.logger = logging.getLogger(__name__)
        
        # Initialize service objects
        base_service = BaseService(base_url, self.headers, self.logger)
        self.auth = AuthService(base_service, self)
        self.schedules = ScheduleService(base_service)
        self.consumables = ConsumableService(base_service)
        self.devices = DeviceService(base_service)
        self.rooms = RoomService(base_service)
        self.scenes = SceneService(base_service)
        self.automations = AutomationService(base_service)
        self.states = StateService(base_service)

    def update_auth_header(self, api_key: str) -> None:
        """Update authorization header with new API key."""
        self.api_key = api_key
        self.headers["Authorization"] = f"Bearer {api_key}"
