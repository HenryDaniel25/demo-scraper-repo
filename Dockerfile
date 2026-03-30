FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

# Copy dependencies first (better caching)
COPY requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Ensure logs show immediately in ECS
ENV PYTHONUNBUFFERED=1

# Run script
CMD ["python", "youtube_scraper.py"]