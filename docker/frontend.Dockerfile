FROM node:18-alpine as build

WORKDIR /app

# Install Angular CLI globally
RUN npm install -g @angular/cli

# Copy package.json and package-lock.json if they exist
COPY ./package*.json ./

# Install dependencies
RUN npm install

# Copy all files from context
COPY . .

# Build the app in production mode
RUN ng build --configuration production

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Install timezone data
RUN apk add --no-cache tzdata

# Set timezone to Asia/Taipei
ENV TZ=Asia/Taipei
RUN cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime && echo "Asia/Taipei" > /etc/timezone

# Copy built app from previous stage
COPY --from=build /app/dist/smart-home-assistant-web /usr/share/nginx/html

# Copy both configuration files - one for local Docker, one for Azure
COPY ./nginx.conf /etc/nginx/conf.d/local.conf.template
COPY ./nginx.azure.conf /etc/nginx/conf.d/azure.conf.template

# Install envsubst for environment variable support
RUN apk add --no-cache gettext bash

# Create a simple startup script to select the right configuration based on environment
RUN echo '#!/bin/bash' > /docker-entrypoint.sh && \
    echo 'set -e' >> /docker-entrypoint.sh && \
    echo 'if [ -n "$BACKEND_URL" ]; then' >> /docker-entrypoint.sh && \
    echo '  echo "Running in Azure Container Apps mode with BACKEND_URL: $BACKEND_URL"' >> /docker-entrypoint.sh && \
    echo '  envsubst "\$BACKEND_URL" < /etc/nginx/conf.d/azure.conf.template > /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.sh && \
    echo 'else' >> /docker-entrypoint.sh && \
    echo '  echo "Running in local Docker Compose mode"' >> /docker-entrypoint.sh && \
    echo '  cp /etc/nginx/conf.d/local.conf.template /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.sh && \
    echo 'fi' >> /docker-entrypoint.sh && \
    echo 'exec nginx -g "daemon off;"' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

EXPOSE 80

# Use startup script as entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
