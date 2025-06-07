#!/bin/sh

# Smart configuration selection based on environment
if [ ! -z "$BACKEND_URL" ]; then
    echo "Configuring for Azure Container Apps with BACKEND_URL: $BACKEND_URL"
    
    # Prepare nginx config environment variables 
    export BACKEND_URL=${BACKEND_URL}
    
    # Use the Azure-specific template with environment variable substitution
    envsubst '${BACKEND_URL}' < /etc/nginx/conf.d/azure.conf.template > /etc/nginx/conf.d/default.conf
    
    echo "Nginx configured for Azure Container Apps with BACKEND_URL: $BACKEND_URL"
else
    echo "Running in local Docker Compose mode. Using backend:8000 service name"
    # Use the local Docker Compose configuration
    cp /etc/nginx/conf.d/local.conf.template /etc/nginx/conf.d/default.conf
fi

# Execute CMD
echo "Starting Nginx..."
exec "$@"
