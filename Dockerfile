FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Expose the API port
EXPOSE 8000

# Use start script: waits for DB, runs migrations, starts uvicorn
CMD ["./start.sh"]
