"""Verify server startup, config, and auth provider configuration."""

from app.auth import get_auth_provider
from app.config import Settings, configured_mcp_name, mcp_name


def test_mcp_name_is_tinytim():
    assert mcp_name == "tinytim"
    assert configured_mcp_name() == "tinytim"


def test_settings_defaults():
    s = Settings()
    assert s.SERVICE_ID == "tinytim_mcp"
    assert s.APP_TITLE == "Tinytim MCP"
    assert s.APP_VERSION == "1.0.0"
    assert s.ENVIRONMENT == "development"
    assert s.PORT == 8000


def test_settings_port_from_env():
    import os
    os.environ["PORT"] = "9999"
    try:
        s = Settings()
        assert s.PORT == 9999
    finally:
        del os.environ["PORT"]


def test_auth_provider_uses_configured_jwks_endpoint():
    provider = get_auth_provider()
    assert provider.jwks_uri == "http://account.invalid/.well-known/jwks.json"
    assert provider.algorithm == "RS256"


def test_app_creation_succeeds():
    """verify that create_app() does not raise during import-time setup."""
    from app.main import create_app

    app = create_app()
    assert app is not None
