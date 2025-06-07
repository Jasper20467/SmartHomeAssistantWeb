# Frontend Docker Build - Important Notes

## Configuration Files

The frontend container now uses two different nginx configuration files:

1. **nginx.conf** - Used for local Docker Compose deployment
   - Located in the frontend directory
   - Uses the backend service name for API requests

2. **nginx.azure.conf** - Used for Azure Container Apps deployment
   - Located in both docker and frontend directories
   - Uses the BACKEND_URL environment variable for API requests

## File Placement

For the Docker build to work properly, make sure:

1. **Both** nginx configuration files are in the frontend directory:
   - `frontend/nginx.conf` (for local mode)
   - `frontend/nginx.azure.conf` (for Azure mode)

2. The Dockerfile references these files with the correct paths:
   ```dockerfile
   COPY ./nginx.conf /etc/nginx/conf.d/local.conf.template
   COPY ./nginx.azure.conf /etc/nginx/conf.d/azure.conf.template
   ```

## Environment Variables

The container now uses `BACKEND_URL` instead of `API_URL` for consistency across all configurations:
- Docker Compose: No environment variable needed (uses backend:8000)
- Azure Container Apps: Set BACKEND_URL to the backend FQDN

## Building the Frontend Container

To build the frontend container:

```powershell
# From the project root
docker build -f ./docker/frontend.Dockerfile -t yourusername/homeassistant.frontend:1.0 ./frontend
```

Note that the build context (last parameter) must be the frontend directory.

## Testing

You can test both configurations using:

```powershell
# Test local mode
.\scripts\test_frontend_container.ps1 -TestType local

# Test Azure mode
.\scripts\test_frontend_container.ps1 -TestType azure
```
