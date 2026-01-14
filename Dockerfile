FROM python:3.14-slim

# Install curl for retrieving the uv installer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv using the official installer
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH (installer puts binaries under /root/.local/bin)
ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy the full application
COPY . .

# Install dependencies using uv
RUN uv sync

# Add .venv/bin to PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Expose the MCP port
EXPOSE 9300


# Start the FastMCP HTTP server
# CMD ["fastmcp", "run", "server.py", "--transport", "http", "--port", "9400", "--host", "0.0.0.0"]
CMD ["uvicorn", "server:app", "--port", "9300", "--host", "0.0.0.0", "--timeout-graceful-shutdown", "10", "--limit-concurrency", "100", "--lifespan", "on", "--ws", "websockets-sansio"]
