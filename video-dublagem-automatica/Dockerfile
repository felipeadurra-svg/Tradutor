FROM python:3.11-slim

LABEL maintainer="Felipe <seu-email@example.com>"
LABEL description="Video Dublagem Automática - Automatic video dubbing system"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Verify installations
RUN ffmpeg -version && ffprobe -version

# Create non-root user
RUN useradd -m -u 1000 app_user

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create storage directories
RUN mkdir -p storage/input storage/audio storage/output credentials && \
    chown -R app_user:app_user /app

# Switch to non-root user
USER app_user

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
