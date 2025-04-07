"""
Authentication Service

Handles authentication with the Home Assistant backend.
"""
from typing import Dict, Any

from .base_service import BaseService


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, base_service: BaseService, client):
        """Initialize with base service and client reference."""
        self.base = base_service
        self.client = client
    
    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate with the Home Assistant backend and get an API token."""
        endpoint = "/api/auth/login"
        data = {
            "username": username,
            "password": password
        }
        response = self.base.make_request("POST", endpoint, data)
        if "access_token" in response:
            self.client.update_auth_header(response["access_token"])
        return response
