"""
Schedule Service

Handles schedule-related operations.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base_service import BaseService


class ScheduleService:
    """Service for schedule operations."""
    
    def __init__(self, base_service: BaseService):
        """Initialize with base service."""
        self.base = base_service
    
    def get_schedules(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all schedules with pagination."""
        endpoint = f"/api/schedules?skip={skip}&limit={limit}"
        return self.base.make_request("GET", endpoint)
    
    def create_schedule(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new schedule."""
        endpoint = "/api/schedules"
        return self.base.make_request("POST", endpoint, schedule_data)
    
    def update_schedule(self, schedule_id: str, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing schedule."""
        endpoint = f"/api/schedules/{schedule_id}"
        return self.base.make_request("PUT", endpoint, schedule_data)
    
    def delete_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Delete a schedule."""
        endpoint = f"/api/schedules/{schedule_id}"
        return self.base.make_request("DELETE", endpoint)
    
    def get_schedule_by_id(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Get a schedule by its ID."""
        endpoint = f"/api/schedules/{schedule_id}"
        return self.base.make_request("GET", endpoint)