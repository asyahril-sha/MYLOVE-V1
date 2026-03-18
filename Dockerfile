FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust compiler
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies satu per satu
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir aiohttp==3.9.5
RUN pip install --no-cache-dir python-telegram-bot==20.7
RUN pip install --no-cache-dir pydantic==2.5.0
RUN pip install --no-cache-dir pydantic-settings==2.1.0
RUN pip install --no-cache-dir aiosqlite==0.19.0
RUN pip install --no-cache-dir sqlalchemy==2.0.23
RUN pip install --no-cache-dir numpy==1.24.3
RUN pip install --no-cache-dir loguru==0.7.2
RUN pip install --no-cache-dir aiofiles==23.2.0
RUN pip install --no-cache-dir httpx==0.25.2
RUN pip install --no-cache-dir requests==2.31.0
RUN pip install --no-cache-dir cryptography==41.0.7
RUN pip install --no-cache-dir psutil==5.9.5

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 mylove && chown -R mylove:mylove /app
USER mylove

# Run the application
CMD ["python", "main.py"]
