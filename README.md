# Dataloop MCP


[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=dataloop-ai-mcp&config=eyJjb21tYW5kIjoiZG9ja2VyIHJ1biAtaSAtLXJtIC1lIERBVEFMT09QX0FQSV9LRVkgZG9ja2VyLmlvL2RhdGFsb29wYWkvbWNwOmxhdGVzdCIsImVudiI6eyJEQVRBTE9PUF9BUElfS0VZIjoiIn19)

A Model Context Protocol (MCP) implementation for Dataloop AI that enables seamless integration with the Dataloop platform through a Docker-based stdio interface. MCP provides a standardized way for AI models to interact with their context and environment using standard input/output (stdio) for communication.

## Features

- 🔐 Secure authentication using Dataloop API tokens
- 📚 Direct access to Dataloop documentation and Dataloop platform context
- 🐳 Docker-based deployment

## Prerequisites

- Docker installed on your system
- A Dataloop AI account
- Python 3.10 or higher (for local development)

## Installation

1. **Get your Dataloop API Token**:
   - Log in to the [Dataloop platform](https://console.dataloop.ai)
   - Navigate to Project > API Keys
   - Create a new API token with appropriate permissions

2. **Configure MCP in Cursor**:
   - Open Cursor settings
   - Navigate to MCP configuration
   - Add the following configuration:

```json
{
  "mcpServers": {
    "dataloop-ai-mcp": {
      "command": "docker run -i --rm -e DATALOOP_API_KEY docker.io/dataloopai/mcp:latest",
      "env": {
        "DATALOOP_API_KEY": "<YOUR API TOKEN>"
      }
    }
  }
}
```

## Usage

Once configured, you can interact with the Dataloop MCP through Cursor. The MCP provides the following functionality:

- Ask questions about Dataloop documentation
- Get real-time responses from the Dataloop knowledge base
- Access model context and environment information
- Seamless integration with your development workflow

## Development

### Building the Docker Image

```bash
docker build --no-cache -t docker.io/dataloopai/mcp:latest .
```

### Running Locally

```bash
docker run -i --rm -e DATALOOP_API_KEY=<YOUR_API_TOKEN> docker.io/dataloopai/mcp:latest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.