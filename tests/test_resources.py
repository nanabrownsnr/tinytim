"""Verify the UI resource registration and generated bundle contract.

Add assertions here when changing resource metadata or frontend build output.
"""

import pytest
from fastmcp import FastMCP

from app.ui.notes.resource import VIEW_PATH, VIEW_URI, register_resource


@pytest.mark.asyncio
async def test_notes_ui_resource_is_registered_and_bundled():
    assert VIEW_PATH.is_file(), "Build the UI before running the complete test suite"

    mcp = FastMCP("test-server")
    register_resource(mcp)

    resource = await mcp.get_resource(VIEW_URI)
    html = await resource.read()

    assert "Tinytim Notes MCP App" in html
    assert "tinytim-notes-ui" in html
    assert ".render(React.createElement" not in html


@pytest.mark.asyncio
async def test_view_uri_is_stable():
    assert VIEW_URI == "ui://tinytim/notes.html"
