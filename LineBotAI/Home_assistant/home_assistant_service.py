"""
Legacy Home Assistant Service

This module is maintained for backward compatibility.
"""

import logging
import warnings
from typing import Dict, List, Any, Optional
from datetime import date, datetime

# Import from the package
from .client import HomeAssistantClient

# Display a deprecation warning
warnings.warn(
    "Direct use of home_assistant_service.py is deprecated. "
    "Please use HomeAssistantClient instead.",
    DeprecationWarning,
    stacklevel=2
)

# For backward compatibility
class HomeAssistantService(HomeAssistantClient):
    """Legacy class for backward compatibility."""
    pass
