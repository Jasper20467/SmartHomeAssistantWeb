# Azure Container Apps Deployment Fix Guide
## Docker Container Crash Problem Solution

This document provides step-by-step instructions for deploying the Smart Home Assistant Web application to Azure Container Apps after fixing the Nginx configuration issue that was causing container crashes.

## Problem Summary

The frontend container was crashing in Azure Container Apps with the error:
```
host not found in upstream 'backend'
```

This occurred because the Nginx configuration in the frontend container was hardcoded to use the hostname "backend:8000", which works in Docker Compose environments but not in Azure Container Apps.

## Solution Implemented

We implemented a dual-configuration approach that works in both environments:

1. Created two Nginx configuration files:
   - Local Docker Compose: Uses DNS resolution of "backend" service name
   - Azure: Uses BACKEND_URL environment variable injected by our deployment

2. Added a smart startup script that checks for environment variables and selects the appropriate configuration at container startup

3. Changed environment variable naming from API_URL to BACKEND_URL for clarity

## Testing the Fix Locally

Before deploying to Azure, you can test both configurations locally:

```powershell
# Test the local Docker Compose configuration (uses backend:8000)
.\scripts\test_frontend_container.ps1 -TestType local

# Test the Azure Container Apps configuration (uses BACKEND_URL)
.\scripts\test_frontend_container.ps1 -TestType azure
```

## Deployment Steps

### 1. Build and Push Updated Docker Images

```powershell
# Build the updated images
docker build -f ./docker/frontend.Dockerfile -t yourusername/homeassistant.frontend:1.0 ./frontend
docker build -f ./docker/backend.Dockerfile -t yourusername/homeassistant.backend:1.0 ./backend

# Push to Docker Hub (or your container registry)
docker push yourusername/homeassistant.frontend:1.0
docker push yourusername/homeassistant.backend:1.0
```

### 2. Update the main.bicep File

The main.bicep file has already been updated to use BACKEND_URL environment variable instead of API_URL.

### 3. Deploy to Azure Container Apps

```powershell
cd infra
./deploy_container_apps.ps1 -ResourceGroupName JYSmartHomeAssistant -AppName jyhomeassistant
```

### 4. Verify the Deployment

1. Wait for the deployment to complete (usually 5-10 minutes)
2. Open the frontend URL provided in the deployment output
3. Check that the application loads and can communicate with the backend API
4. Check frontend container logs for any issues

### 5. Troubleshooting

If issues persist:

```powershell
cd infra
./troubleshoot_container_apps.ps1 -ResourceGroupName JYSmartHomeAssistant -AppName jyhomeassistant
```

This script will:
- Show container statuses
- Display frontend logs
- Offer to fix the BACKEND_URL environment variable if needed
- Restart the frontend container after applying fixes

## Understanding the Technical Fix

1. **Docker nginx.conf (for local deployment):**
   - Uses Docker's built-in DNS resolver (127.0.0.11)
   - Sets hostname to "backend:8000"

2. **Azure nginx.conf (for Azure deployment):**
   - Uses BACKEND_URL environment variable
   - Still includes resolver configuration for completeness

3. **Startup Script Logic:**
```bash
if [ -n "$BACKEND_URL" ]; then
  # Use Azure configuration with environment variable
  envsubst "$BACKEND_URL" < /etc/nginx/conf.d/azure.conf.template > /etc/nginx/conf.d/default.conf
else
  # Use local Docker Compose configuration
  cp /etc/nginx/conf.d/local.conf.template /etc/nginx/conf.d/default.conf
fi
```

## Conclusion

With these changes, the frontend container now works correctly in both local Docker Compose and Azure Container Apps environments, without requiring any manual configuration changes when moving between environments.
