"""
Consumable Service

Handles consumable-related operations.
"""
from typing import Dict, List, Any, Optional
from datetime import date

from .base_service import BaseService


class ConsumableService:
    """Service for consumable operations."""
    
    def __init__(self, base_service: BaseService):
        """Initialize with base service."""
        self.base = base_service
    
    def get_consumables(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all consumables with pagination."""
        endpoint = f"/api/consumables?skip={skip}&limit={limit}"
        return self.base.make_request("GET", endpoint)
    
    def get_consumable_by_id(self, consumable_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific consumable by its ID."""
        endpoint = f"/api/consumables/{consumable_id}"
        return self.base.make_request("GET", endpoint)
    
    def create_consumable(self, consumable_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new consumable."""
        endpoint = "/api/consumables"
        return self.base.make_request("POST", endpoint, json=consumable_data)
    
    def update_consumable(self, consumable_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing consumable."""
        endpoint = f"/api/consumables/{consumable_id}"
        return self.base.make_request("PUT", endpoint, json=update_data)
    
    def delete_consumable(self, consumable_id: str) -> None:
        """Delete a consumable by its ID."""
        endpoint = f"/api/consumables/{consumable_id}"
        self.base.make_request("DELETE", endpoint)