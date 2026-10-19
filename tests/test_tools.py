"""Verify the notes tools: create, list, get, validation, and metadata.

Use this test shape for every tool-to-App contract added to tinytim.
"""

import pytest
from fastmcp import FastMCP

from app.tools.notes import register_tool
from app.ui.notes.resource import VIEW_URI


@pytest.fixture
def mcp_instance():
    """Create an isolated MCP server containing the notes tool."""
    mcp = FastMCP("test-server")
    register_tool(mcp)
    return mcp


@pytest.mark.asyncio
async def test_create_note_returns_text_and_ui_data(mcp_instance):
    tool = await mcp_instance.get_tool("create_note")

    result = await tool.run({"title": "Test Note", "body": "Hello world"})

    assert tool.meta["ui"]["resourceUri"] == VIEW_URI
    assert tool.meta["ui"]["visibility"] == ["model", "app"]
    assert result.content[0].text == 'Note "Test Note" created successfully.'
    sc = result.structured_content
    assert "note" in sc
    assert "structured_content" in sc
    note = sc["note"]
    assert note["title"] == "Test Note"
    assert note["body"] == "Hello world"
    assert note["tags"] == []
    assert "id" in note
    assert "created_at" in note
    assert note["status"] == "created"
    assert result.meta["ui"]["resourceUri"] == VIEW_URI
    assert result.meta["ui/resourceUri"] == VIEW_URI


@pytest.mark.asyncio
async def test_create_note_with_tags(mcp_instance):
    tool = await mcp_instance.get_tool("create_note")

    result = await tool.run({
        "title": "Tagged Note",
        "body": "Has tags",
        "tags": ["work", "idea"],
    })

    sc = result.structured_content
    assert sc["note"]["tags"] == ["work", "idea"]


@pytest.mark.asyncio
async def test_create_note_empty_title_raises(mcp_instance):
    tool = await mcp_instance.get_tool("create_note")

    with pytest.raises(ValueError, match="title must be a non-empty string"):
        await tool.run({"title": "", "body": "some body"})


@pytest.mark.asyncio
async def test_create_note_empty_body_raises(mcp_instance):
    tool = await mcp_instance.get_tool("create_note")

    with pytest.raises(ValueError, match="body must be a non-empty string"):
        await tool.run({"title": "A title", "body": ""})


@pytest.mark.asyncio
async def test_create_note_whitespace_only_title_raises(mcp_instance):
    tool = await mcp_instance.get_tool("create_note")

    with pytest.raises(ValueError, match="title must be a non-empty string"):
        await tool.run({"title": "   ", "body": "some body"})


@pytest.mark.asyncio
async def test_create_note_whitespace_only_body_raises(mcp_instance):
    tool = await mcp_instance.get_tool("create_note")

    with pytest.raises(ValueError, match="body must be a non-empty string"):
        await tool.run({"title": "A title", "body": "  "})


@pytest.mark.asyncio
async def test_create_note_trims_whitespace(mcp_instance):
    tool = await mcp_instance.get_tool("create_note")

    result = await tool.run({"title": "  Trimmed  ", "body": "  content  "})

    sc = result.structured_content
    assert sc["note"]["title"] == "Trimmed"
    assert sc["note"]["body"] == "content"


@pytest.mark.asyncio
async def test_list_notes_empty(mcp_instance):
    tool = await mcp_instance.get_tool("list_notes")

    result = await tool.run({})

    sc = result.structured_content
    assert sc["count"] == 0
    assert sc["notes"] == []
    assert isinstance(sc, dict)


@pytest.mark.asyncio
async def test_list_notes_after_creations(mcp_instance):
    create_tool = await mcp_instance.get_tool("create_note")
    list_tool = await mcp_instance.get_tool("list_notes")

    await create_tool.run({"title": "Note One", "body": "First"})
    await create_tool.run({"title": "Note Two", "body": "Second"})

    result = await list_tool.run({})

    sc = result.structured_content
    assert sc["count"] == 2
    assert len(sc["notes"]) == 2
    assert sc["notes"][0]["title"] == "Note One"
    assert sc["notes"][1]["title"] == "Note Two"


@pytest.mark.asyncio
async def test_list_notes_structured_content_is_object(mcp_instance):
    """The structured_content must be an object (dict), never a bare list."""
    list_tool = await mcp_instance.get_tool("list_notes")

    result = await list_tool.run({})

    assert isinstance(result.structured_content, dict)
    assert "count" in result.structured_content
    assert "notes" in result.structured_content


@pytest.mark.asyncio
async def test_get_note_found(mcp_instance):
    create_tool = await mcp_instance.get_tool("create_note")
    get_tool = await mcp_instance.get_tool("get_note")

    create_result = await create_tool.run({"title": "Get Me", "body": "Body"})
    note_id = create_result.structured_content["note"]["id"]

    result = await get_tool.run({"note_id": note_id})

    assert result.content[0].text == "Get Me"
    sc = result.structured_content
    assert sc["note"]["id"] == note_id
    assert sc["note"]["title"] == "Get Me"


@pytest.mark.asyncio
async def test_get_note_not_found_raises(mcp_instance):
    get_tool = await mcp_instance.get_tool("get_note")

    with pytest.raises(ValueError, match="Note not found: deadbeef"):
        await get_tool.run({"note_id": "deadbeef"})


@pytest.mark.asyncio
async def test_get_note_returns_stable_id_and_timestamps(mcp_instance):
    create_tool = await mcp_instance.get_tool("create_note")
    get_tool = await mcp_instance.get_tool("get_note")

    result = await create_tool.run({"title": "Timestamped", "body": "Time"})
    note_id = result.structured_content["note"]["id"]
    created_at = result.structured_content["note"]["created_at"]

    get_result = await get_tool.run({"note_id": note_id})

    assert get_result.structured_content["note"]["id"] == note_id
    assert get_result.structured_content["note"]["created_at"] == created_at


@pytest.mark.asyncio
async def test_tool_metadata_matches_view_uri(mcp_instance):
    """The create_note tool must carry the correct UI resource URI in meta."""
    create_tool = await mcp_instance.get_tool("create_note")

    result = await create_tool.run({"title": "Meta", "body": "Test"})

    assert result.meta["ui"]["resourceUri"] == VIEW_URI
    assert result.meta["ui/resourceUri"] == VIEW_URI
