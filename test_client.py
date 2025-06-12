import asyncio
import os
import requests
from datetime import timedelta
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
import dtlpy as dl

def get_app_jwt() -> str:
    """Get the APP_JWT from the request headers."""
    app_jwt = os.environ.get('APP_JWT', None)
    
    if app_jwt is None or is_expired(app_jwt):
        session = requests.Session()
        response = session.get(
            "https://rc-gate.dataloop.ai/api/v1/apps/dataloop-mcp-68487395868810ae1b6f2490/panels/mcp/",
            headers=dl.client_api.auth
        )
        # The JWT is likely in the cookies after redirects
        app_jwt = session.cookies.get("JWT-APP")
    os.environ['APP_JWT'] = app_jwt
    return app_jwt


# You may need to adjust the server_url if running locally or on a different host
server_url = "https://dataloop-mcp-68487395868810ae1b6f2490.apps-rc.dataloop.ai/mcp/sse"

# Get the app_jwt from environment or set it here for testing
app_jwt = get_app_jwt()

async def main():
    print("[TEST CLIENT] Connecting to MCP server and calling ask_dataloop tool...")
    async with streamablehttp_client(
        server_url, headers={"Cookie": f"JWT-APP={app_jwt}"}
    ) as (read, write, _):
        async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=60)) as session:
            await session.initialize()
            question = "What is Dataloop?"
            tool_result = await session.call_tool("ask_dataloop", {"question": question})
            print("[RESULT]", tool_result)

if __name__ == "__main__":
    asyncio.run(main()) 