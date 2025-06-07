# Docker Configuration for Smart Home Assistant Web

This directory contains Docker configuration files for the Smart Home Assistant Web application.

## Nginx Configuration

The nginx.conf file is now set up to use environment variables for the backend API URL. This makes the frontend container more flexible for different deployment environments:

- In Docker Compose, it uses `http://backend:8000` by default (service discovery)
- In Azure Container Apps, it uses the specified API_URL environment variable

## Entrypoint Script

The `entrypoint.sh` script is used to:
1. Set up the nginx configuration with the correct API_URL at container startup
2. Substitute the environment variables in the nginx config
3. Start nginx with the correct configuration

## Deployment Considerations

### Local Development
For local development with Docker Compose, the default configuration works automatically with service discovery.

### Azure Container Apps
When deploying to Azure Container Apps, make sure to:

1. Build and push your container images with the latest changes
2. Set the API_URL environment variable correctly in the Azure Container App for the frontend
3. The API_URL should be set to the FQDN of the backend container app (e.g., `https://appname-backend.domain.com`)

### Troubleshooting Azure Deployment

If you encounter "host not found in upstream" errors:

1. Run the `troubleshoot_container_apps.ps1` script to diagnose issues
2. Verify that the API_URL environment variable is set correctly
3. Check if the nginx configuration is properly using the environment variables
4. Verify that the backend container app is running and accessible

## Building Images

Build the frontend image:

```
docker build -t smarthome-frontend -f docker/frontend.Dockerfile ./frontend
```

## Testing the Configuration

To test with different API URLs locally:

```
docker run -e API_URL=http://myapi.example.com -p 8080:80 smarthome-frontend
```
