import logging
from typing import Any
import dtlpy as dl
from pydantic_settings import BaseSettings, SettingsConfigDict
from mcp.server.fastmcp import FastMCP, Context
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from datetime import timedelta
import os
import jwt
import time
import requests
import traceback

logger = logging.getLogger("[DATALOOP-MCP]")


class DataloopContext:
    def __init__(self, token: str = None):
        self._token = token
        self.app_jwt = None
        self.app_route_url = None
        self.server_url = None
        if token is not None:
            self.load_app_info()

    @property
    def token(self) -> str:
        if self._token is None:
            raise ValueError("Missing token")
        return self._token

    @token.setter
    def token(self, token: str):
        self._token = token
        self.load_app_info()

    def load_app_info(self) -> str:
        """Get the server URL from the request headers."""
        try:
            dl.client_api.token = self.token
            dpk = dl.dpks.get(dpk_name="dataloop-mcp")
            apps_filters = dl.Filters(field='dpkName', values=dpk.name, resource='apps')
            app = dl.apps.list(filters=apps_filters).items[0]
            logger.info(f"App: {app.name}")
            self.app_route_url = app.routes['mcp']
            # get the redirected url
            session = requests.Session()
            response = session.get(self.app_route_url, headers=dl.client_api.auth)
            logger.info(f"App route URL: {response.url}")
            self.server_url = response.url
            self.app_jwt = session.cookies.get("JWT-APP")
        except Exception as e:
            raise ValueError(f"Failed getting app info: {traceback.format_exc()}")

    @staticmethod
    def is_expired(app_jwt: str) -> bool:
        """Check if the APP_JWT is expired."""
        try:
            decoded = jwt.decode(app_jwt, options={"verify_signature": False})
            if decoded.get("exp") < time.time():
                return True
            return False
        except jwt.ExpiredSignatureError:
            return True
        except Exception as e:
            logger.error(f"Error decoding JWT: {e}")
            return True

    def get_app_jwt(self) -> str:
        """Get the APP_JWT from the request headers."""

        if self.app_jwt is None or self.is_expired(self.app_jwt):
            try:
                dl.client_api.token = self.token
                session = requests.Session()
                response = session.get(self.app_route_url, headers=dl.client_api.auth)
                # The JWT is likely in the cookies after redirects
                self.app_jwt = session.cookies.get("JWT-APP")
            except Exception as e:
                raise ValueError(f"Failed getting app JWT from cookies: {traceback.format_exc()}")
        if not self.app_jwt:
            raise ValueError(
                "APP_JWT is missing. Please set the APP_JWT environment variable or ensure authentication is working."
            )
        return self.app_jwt

    @staticmethod
    def user_info(token: str):
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded
        except Exception as e:
            raise ValueError(f"Failed getting user info: {traceback.format_exc()}")


class ServerSettings(BaseSettings):
    """Settings for the Dataloop MCP server."""

    model_config = SettingsConfigDict(env_prefix="MCP_DATALOOP_")

    def __init__(self, **data):
        super().__init__(**data)


def create_dataloop_mcp_server(settings: ServerSettings) -> FastMCP:
    """Create a FastMCP server for Dataloop with Bearer token authentication."""

    app = FastMCP(
        name="Dataloop MCP Server",
        instructions="A multi-tenant MCP server for Dataloop with authentication",
        stateless_http=True,
        debug=True,
    )
    dl_context = DataloopContext(token=os.environ.get('DATALOOP_API_KEY'))

    @app.tool(description="Ask the Dataloop docs")
    async def ask_dataloop(question: str, ctx: Context) -> dict[str, Any]:
        """Ask the Dataloop documentation.
        Args:
            question: The question to ask
        """
        try:
            app_jwt = dl_context.get_app_jwt()
            server_url = dl_context.server_url
            headers = {"Cookie": f"JWT-APP={app_jwt}", "x-dl-info": f"{dl_context.token}"}
            # Create a session using the client streams
            async with streamablehttp_client(server_url, headers=headers) as (read, write, _):
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=60)) as session:
                    # Initialize the connection
                    await session.initialize()
                    # Call a tool
                    tool_result = await session.call_tool("ask_dataloop", {"question": question})
                    return tool_result
        except Exception as e:
            return {"error": f"Failed to process request: {traceback.format_exc()}"}

    return app


def main() -> int:
    logger.info("Starting Dataloop MCP server in stdio mode")

    try:
        settings = ServerSettings()
        logger.info("Successfully configured Dataloop MCP server")

    except Exception as e:
        logger.error(f"Unexpected error during startup:\n{traceback.format_exc()}")
        return 1

    try:
        mcp_server = create_dataloop_mcp_server(settings)
        logger.info("Starting Dataloop MCP server in stdio mode")
        logger.info("Users should provide their API key in the Authorization header as a Bearer token")
        mcp_server.run(transport="stdio")
        return 0
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        return 1


if __name__ == "__main__":
    main()
