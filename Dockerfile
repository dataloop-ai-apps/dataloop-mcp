FROM docker.io/dataloopai/dtlpy-agent:cpu.py3.10.opencv

# Set working directory
WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY test_client.py .

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Start the application (stdio-based, not HTTP)
CMD ["python", "main.py"]

# Build image:
# docker build --no-cache -t docker.io/dataloopai/mcp:latest .

# Push to registry:
# docker push docker.io/dataloopai/mcp:latest

# Run container:
# docker run -i --rm -e DATALOOP_API_KEY=<YOUR_API_TOKEN> docker.io/dataloopai/mcp:latest