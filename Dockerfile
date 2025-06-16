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
# docker build -t docker.io/dataloopai/mcp:0.0.6 .

# Push to registry:
# docker tag docker.io/dataloopai/mcp:0.0.6 docker.io/dataloopai/mcp:latest
# docker push docker.io/dataloopai/mcp:0.0.6
# docker push docker.io/dataloopai/mcp:latest

# Run container:
# docker run -i --rm -e DATALOOP_API_KEY=<YOUR_API_TOKEN> docker.io/dataloopai/mcp:latest