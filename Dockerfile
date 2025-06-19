FROM docker.io/dataloopai/dtlpy-agent:cpu.py3.10.opencv

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .  

# Start the application (stdio-based, not HTTP)
CMD ["python", "main.py"]

# Build image:
# docker build -t docker.io/dataloopai/mcp:0.0.7 .
# docker build -t docker.io/dataloopai/mcp:latest .

# Push to registry:
# docker push docker.io/dataloopai/mcp:0.0.7
# docker push docker.io/dataloopai/mcp:latest

# Run container:
# docker run -i --rm -e DATALOOP_API_KEY=<YOUR_API_TOKEN> docker.io/dataloopai/mcp:latest