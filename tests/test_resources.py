"""Verify the UI resource registration and generated bundle contract.

Add assertions here when changing resource metadata or frontend build output.
"""

import pytest
from fastmcp import FastMCP

from app.ui.notes.create.resource import CREATE_PATH, CREATE_URI
from app.ui.notes.detail.resource import DETAIL_PATH, DETAIL_URI
from app.ui.notes.list.resource import LIST_PATH, LIST_URI
from app.ui.notes.resource import (
    VIEW_URI,
    load_create_html,
    load_detail_html,
    load_list_html,
    load_view_html,
    register_resource,
)


@pytest.mark.asyncio
async def test_list_ui_resource_is_registered_and_bundled():
    assert LIST_PATH.is_file(), "Build the list UI before running the complete test suite"

    mcp = FastMCP("test-server")
    register_resource(mcp)

    resource = await mcp.get_resource(LIST_URI)
    html = await resource.read()

    assert "Tinytim List Notes MCP App" in html
    assert "tinytim-notes-list-ui" in html
    assert ".render(React.createElement" not in html


@pytest.mark.asyncio
async def test_create_ui_resource_is_registered_and_bundled():
    assert CREATE_PATH.is_file(), "Build the create UI before running the complete test suite"

    mcp = FastMCP("test-server")
    register_resource(mcp)

    resource = await mcp.get_resource(CREATE_URI)
    html = await resource.read()

    assert "Tinytim Create Note MCP App" in html
    assert "tinytim-notes-create-ui" in html
    assert ".render(React.createElement" not in html


@pytest.mark.asyncio
async def test_detail_ui_resource_is_registered_and_bundled():
    assert DETAIL_PATH.is_file(), "Build the detail UI before running the complete test suite"

    mcp = FastMCP("test-server")
    register_resource(mcp)

    resource = await mcp.get_resource(DETAIL_URI)
    html = await resource.read()

    assert "Tinytim Note Detail MCP App" in html
    assert "tinytim-notes-detail-ui" in html
    assert ".render(React.createElement" not in html


@pytest.mark.asyncio
async def test_view_uri_is_stable():
    assert VIEW_URI == "ui://tinytim/notes.html"


@pytest.mark.asyncio
async def test_list_uri_is_stable():
    assert LIST_URI == "ui://tinytim/notes/list.html"


@pytest.mark.asyncio
async def test_create_uri_is_stable():
    assert CREATE_URI == "ui://tinytim/notes/create.html"


@pytest.mark.asyncio
async def test_detail_uri_is_stable():
    assert DETAIL_URI == "ui://tinytim/notes/detail.html"


@pytest.mark.asyncio
async def test_all_resources_registered_on_same_mcp():
    """All three UI resources should be registerable on the same MCP server."""
    mcp = FastMCP("test-server")
    register_resource(mcp)

    list_resource = await mcp.get_resource(LIST_URI)
    list_html = await list_resource.read()
    assert "Tinytim List Notes MCP App" in list_html

    create_resource = await mcp.get_resource(CREATE_URI)
    create_html = await create_resource.read()
    assert "Tinytim Create Note MCP App" in create_html

    detail_resource = await mcp.get_resource(DETAIL_URI)
    detail_html = await detail_resource.read()
    assert "Tinytim Note Detail MCP App" in detail_html


@pytest.mark.asyncio
async def test_load_functions_return_html():
    """All load functions should return non-empty HTML strings."""
    assert len(load_list_html()) > 0
    assert len(load_create_html()) > 0
    assert len(load_detail_html()) > 0
    assert len(load_view_html()) > 0


@pytest.mark.asyncio
async def test_view_uri_aliased_to_list_html():
    """VIEW_URI (backward-compatible) should return the same HTML as LIST_URI."""
    mcp = FastMCP("test-server")
    register_resource(mcp)

    view_resource = await mcp.get_resource(VIEW_URI)
    view_html = await view_resource.read()

    list_resource = await mcp.get_resource(LIST_URI)
    list_html = await list_resource.read()

    assert view_html == list_html
