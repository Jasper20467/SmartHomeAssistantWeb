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

# Copy nginx configuration - works for both debug and production
# In production, Caddy handles API routing, so nginx only serves static files
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
