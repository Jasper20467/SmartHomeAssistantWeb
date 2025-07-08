import os

def get_backend_url():
    """Get backend URL based on environment configuration"""
    # Check if custom backend URL is provided
    custom_url = os.getenv('BACKEND_API_URL')
    if custom_url and custom_url.strip():
        return custom_url
    
    # Determine URL based on environment
    debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    debug_stage = os.getenv('DEBUG_STAGE', 'false').lower() == 'true'
    
    if debug_mode or debug_stage:
        # Debug mode: use direct container communication
        return 'http://backend:8000'
    else:
        # Production mode: use domain URL through Caddy proxy
        domain = os.getenv('DOMAIN_NAME', 'smarthome.the-jasperezlife.com')
        if not domain or domain.strip() == '':
            domain = 'smarthome.the-jasperezlife.com'
        return f'https://{domain}/api'
