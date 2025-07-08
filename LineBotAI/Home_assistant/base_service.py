"""
Base Service

Contains common functionality for all service classes.
"""
import json
import requests
import logging
from typing import Dict, Any

class BaseService:
    """Base service class with common functionality for API calls."""
    
    def __init__(self, base_url: str, headers: Dict[str, str], logger: logging.Logger):
        """Initialize with base URL, headers, and logger."""
        self.base_url = base_url
        self.headers = headers
        self.logger = logger
    
    def make_request(self, method: str, endpoint: str, data: Any = None) -> Dict[str, Any]:
        """Make HTTP request to the backend API."""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()  # Raise exception for error status codes
            
            # Handle empty responses (like 204 No Content)
            if response.status_code == 204 or not response.content:
                return {"success": True, "message": "操作成功完成"}
            
            try:
                return response.json()
            except json.JSONDecodeError:
                # If we can't parse JSON but the status is OK, return success
                if response.status_code < 400:
                    return {"success": True, "message": "操作成功完成"}
                else:
                    self.logger.error(f"Failed to decode JSON response from {url}")
                    return {"error": "Invalid JSON response"}
                    
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error: {e}")
            return {"error": str(e)}
