FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust compiler (for pydantic-core)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .

# ===== FORCE INSTALL AIOHTTP =====
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir aiohttp==3.9.5
RUN pip install --no-cache-dir -r requirements.txt
# ================================

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 mylove && chown -R mylove:mylove /app
USER mylove

# Run the application
CMD ["python", "main.py"]
