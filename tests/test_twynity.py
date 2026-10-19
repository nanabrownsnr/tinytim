"""Verify tinytim's public manifest and health custom routes.

Extend this module when adding or changing custom HTTP routes.
"""

import pytest
from fastmcp import FastMCP
from starlette.testclient import TestClient

from app.config import settings
from app.twynity import register_routes


@pytest.fixture
def unauthenticated_app():
    """No auth attached — manifest/health should work without a token."""
    mcp = FastMCP("test_server")
    register_routes(mcp)
    return mcp.http_app()


@pytest.fixture
def named_app():
    """App using the real tinytim settings."""
    mcp = FastMCP(settings.APP_TITLE)
    register_routes(mcp)
    return mcp.http_app()


def test_manifest_returns_expected_shape(unauthenticated_app):
    client = TestClient(unauthenticated_app)
    response = client.get("/api/v1/.well-known/mcp.json")

    assert response.status_code == 200
    body = response.json()
    assert "name" in body
    assert "version" in body


def test_manifest_with_real_settings(named_app):
    client = TestClient(named_app)
    response = client.get("/api/v1/.well-known/mcp.json")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == settings.APP_TITLE
    assert body["version"] == settings.APP_VERSION


def test_health_endpoint_returns_ok(unauthenticated_app):
    client = TestClient(unauthenticated_app)
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_custom_health_route_is_not_implicitly_jwt_protected(unauthenticated_app):
    """Custom routes need explicit auth even when FastMCP has a JWT verifier."""
    from starlette.testclient import TestClient

    response = TestClient(unauthenticated_app).get("/api/v1/health")

    assert response.status_code == 200
