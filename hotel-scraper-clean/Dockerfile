# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libxss1 \
    libgconf-2-4 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrender1 \
    libxtst6 \
    libglib2.0-0 \
    libnss3 \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (only Chromium and Firefox to save space)
RUN playwright install chromium firefox
RUN playwright install-deps chromium firefox

# Copy application code
COPY ALL_HOTEL/ ./ALL_HOTEL/
COPY trip_test.py .

# Change to ALL_HOTEL directory for the app
WORKDIR /app/ALL_HOTEL

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "unified_backend:app", "--host", "0.0.0.0", "--port", "8000"]
