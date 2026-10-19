"""Define service identity, environment settings, and logging.

Tinytim uses safe local defaults so the server runs without external
credentials. Extend ``Settings`` when new configuration is needed.
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

mcp_name = "tinytim"


def configured_mcp_name() -> str:
    return mcp_name.strip() or "tinytim"


def configure_logging():
    os.makedirs("./logs", exist_ok=True)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    handler = TimedRotatingFileHandler(
        filename=f"./logs/{configured_mcp_name()}-mcp.log",
        when="midnight",
        interval=1,
        backupCount=7,
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    detailed_handler = TimedRotatingFileHandler(
        filename=f"./logs/{configured_mcp_name()}-mcp-detailed.log",
        when="midnight",
        interval=1,
        backupCount=7,
    )
    detailed_handler.setFormatter(formatter)
    detailed_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(detailed_handler)


class Settings(BaseSettings):
    SERVICE_ID: str = f"{configured_mcp_name()}_mcp"
    APP_TITLE: str = f"{configured_mcp_name().title()} MCP"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: str = "*"
    RELEASE_ID: str = "1.0.0"
    PERSONA_ID_HEADER: str = "Persona-Id"
    PORT: int = int(os.getenv("PORT", "8000"))

    # These fields are required by the template auth/config contracts but
    # the production credential integrations are intentionally skipped for
    # local and test builds. They receive safe placeholder values.
    USAGE_REPORT_ENDPOINT: str = "http://usage.invalid/report"
    ACCOUNT_SERVICE_URL: str = "http://account.invalid"
    ACCOUNT_SERVICE_JWKS_ENDPOINT: str = "/.well-known/jwks.json"
    ACCOUNT_SERVICE_JWKS_CACHE_TTL: int = 300
    LICENSE_KEY: str = "test-license"
    LICENSE_SERVER_BASE_URL: str = "http://license.invalid"
    LICENSE_SERVER_JWKS_ENDPOINT: str = "/.well-known/jwks.json"
    LICENSE_SERVER_ACTIVATION_ENDPOINT: str = "/activate"


settings = Settings()
configure_logging()
