FROM python:3.10-slim

# Install timezone data and set timezone
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

# Install dependencies
COPY LineBotAI/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY LineBotAI/ .

# Set environment variables for configuration
ENV LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token \
    CHATGPT_API_KEY=your_chatgpt_api_key \
    BACKEND_API_URL=http://backend:8000 \
    DOMAIN_NAME=localhost \
    FLASK_ENV=production \
    DEBUG_MODE=false \
    DEBUG_STAGE=false

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
