"""Provide safe environment defaults and shared fixtures for tests.

Tests use local placeholders so contributors do not need private infrastructure
or a .env file.
"""

import os

import pytest

os.environ.setdefault("USAGE_REPORT_ENDPOINT", "http://usage.invalid/report")
os.environ.setdefault("ACCOUNT_SERVICE_URL", "http://account.invalid")
os.environ.setdefault("ACCOUNT_SERVICE_JWKS_ENDPOINT", "/.well-known/jwks.json")
os.environ.setdefault("ACCOUNT_SERVICE_JWKS_CACHE_TTL", "300")
os.environ.setdefault("LICENSE_KEY", "test-license")
os.environ.setdefault("LICENSE_SERVER_BASE_URL", "http://license.invalid")
os.environ.setdefault("LICENSE_SERVER_JWKS_ENDPOINT", "/.well-known/jwks.json")
os.environ.setdefault("LICENSE_SERVER_ACTIVATION_ENDPOINT", "/activate")


@pytest.fixture(autouse=True)
def reset_note_store():
    """Reset the in-memory note store before and after each test."""
    from app.tools import notes

    with notes._notes_lock:
        notes._notes_store.clear()

    yield

    with notes._notes_lock:
        notes._notes_store.clear()
