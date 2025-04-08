"""
Device Service

Handles operations related to devices in the Smart Home Assistant.
"""

class DeviceService:
    """Service for managing devices."""

    def __init__(self, base_service):
        """Initialize the DeviceService with a base service."""
        self.base_service = base_service

    def get_devices(self):
        """Retrieve a list of devices."""
        return self.base_service.get("/devices")

    def get_device_by_id(self, device_id):
        """Retrieve a specific device by its ID."""
        return self.base_service.get(f"/devices/{device_id}")

    def create_device(self, device_data):
        """Create a new device."""
        return self.base_service.post("/devices", json=device_data)

    def update_device(self, device_id, device_data):
        """Update an existing device."""
        return self.base_service.put(f"/devices/{device_id}", json=device_data)

    def delete_device(self, device_id):
        """Delete a device."""
        return self.base_service.delete(f"/devices/{device_id}")
