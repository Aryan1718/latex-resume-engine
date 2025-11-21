FROM --platform=linux/amd64 python:3.12-slim

# Install basic tools + tectonic dependency libgraphite2-3
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    tar \
    libgraphite2-3 \
    && rm -rf /var/lib/apt/lists/*

# Install tectonic with official installer
RUN curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh \
    && mv tectonic /usr/local/bin/tectonic \
    && chmod +x /usr/local/bin/tectonic
# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app ./app

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
