import logging
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parents[1]  # Adjust to point to the correct parent directory
sys.path.insert(0, str(project_root))  # Use insert(0) to prioritize this path

from Home_assistant.client import HomeAssistantClient  # Adjusted import path

# Initialize HomeAssistantClient
BACKEND_API_URL = "http://localhost:8000"  # Replace with actual backend URL
home_assistant_client = HomeAssistantClient(base_url=BACKEND_API_URL)

logger = logging.getLogger(__name__)

def call_chatgpt_api(api_key, message):
    """Call the ChatGPT API with the given message."""
    # ...implementation for calling ChatGPT API...
    return {"response": "ChatGPT response"}


def call_backend_api(category, operate, content):
    """Call the backend API using HomeAssistantClient services."""
    try:
        # Map category to HomeAssistantClient services
        service_map = {
            "schedules": home_assistant_client.schedules,
            "consumables": home_assistant_client.consumables,
        }

        if category not in service_map:
            return {"error": f"Unsupported category: {category}"}

        service = service_map[category]

        # Route operation to the appropriate service method
        if operate == "GET":
            if "id" in content:
                return service.get_schedule_by_id(content["id"]) if category == "schedules" else service.get_consumable_by_id(content["id"])
            return service.get_schedules() if category == "schedules" else service.get_consumables()
        elif operate == "POST":
            return service.create_schedule(content) if category == "schedules" else service.create_consumable(content)
        elif operate == "PUT":
            return service.update_schedule(content["id"], content) if category == "schedules" else service.update_consumable(content["id"], content)
        elif operate == "DELETE":
            return service.delete_schedule(content["id"]) if category == "schedules" else service.delete_consumable(content["id"])
        else:
            return {"error": f"Unsupported operation: {operate}"}
    except Exception as e:
        logger.error(f"Error in call_backend_api: {e}")
        return {"error": str(e)}

def validate_request_format(request_data):
    """Validate the format of the incoming request."""
    # Placeholder for request validation logic
    return True
