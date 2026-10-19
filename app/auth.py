"""Configure JWT verification for MCP requests.

For local and test builds the verifier points at an unreachable JWKS URL so
no external calls are made during startup. Production deployments should
override the account-service settings in the environment.
"""

from fastmcp.server.auth.providers.jwt import JWTVerifier

from app.config import settings


def get_auth_provider():
    """Build the auth checker FastMCP will run on every incoming request."""
    jwks_url = (
        f"{settings.ACCOUNT_SERVICE_URL.rstrip('/')}/"
        f"{settings.ACCOUNT_SERVICE_JWKS_ENDPOINT.lstrip('/')}"
    )
    return JWTVerifier(
        jwks_uri=jwks_url,
    )
