FROM node:18-alpine

WORKDIR /app

# Install Angular CLI globally
RUN npm install -g @angular/cli

# Copy package.json and package-lock.json if they exist
COPY ./package*.json ./

# Install dependencies
RUN npm install

# Copy all files from context
COPY . .

EXPOSE 4200

# Use a shell to create necessary components and setup routing
CMD ["/bin/sh", "-c", "ng serve --host 0.0.0.0"]
