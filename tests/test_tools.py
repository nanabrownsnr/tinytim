"""Verify the notes tools: create, list, get, validation, and metadata.

Use this test shape for every tool-to-App contract added to tinytim.
"""

import pytest
from fastmcp import FastMCP

from app.tools.notes import register_tool
from app.ui.notes.create.resource import CREATE_URI
from app.ui.notes.detail.resource import DETAIL_URI
from app.ui.notes.list.resource import LIST_URI


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

    assert tool.meta["ui"]["resourceUri"] == CREATE_URI
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
    assert result.meta["ui"]["resourceUri"] == CREATE_URI
    assert result.meta["ui/resourceUri"] == CREATE_URI


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
async def test_create_note_tool_metadata_matches_create_uri(mcp_instance):
    """The create_note tool must carry the create UI resource URI in meta."""
    create_tool = await mcp_instance.get_tool("create_note")

    result = await create_tool.run({"title": "Meta", "body": "Test"})

    assert result.meta["ui"]["resourceUri"] == CREATE_URI
    assert result.meta["ui/resourceUri"] == CREATE_URI


@pytest.mark.asyncio
async def test_list_notes_tool_metadata_matches_list_uri(mcp_instance):
    """The list_notes tool must carry the list UI resource URI in meta."""
    list_tool = await mcp_instance.get_tool("list_notes")

    result = await list_tool.run({})

    assert result.meta["ui"]["resourceUri"] == LIST_URI
    assert result.meta["ui/resourceUri"] == LIST_URI


@pytest.mark.asyncio
async def test_get_note_tool_metadata_matches_detail_uri(mcp_instance):
    """The get_note tool must carry the detail UI resource URI in meta."""
    get_tool = await mcp_instance.get_tool("get_note")

    create_tool = await mcp_instance.get_tool("create_note")
    create_result = await create_tool.run({"title": "Detail", "body": "Test"})
    note_id = create_result.structured_content["note"]["id"]

    result = await get_tool.run({"note_id": note_id})

    assert result.meta["ui"]["resourceUri"] == DETAIL_URI
    assert result.meta["ui/resourceUri"] == DETAIL_URI


@pytest.mark.asyncio
async def test_each_tool_has_unique_ui_resource_uri(mcp_instance):
    """Each tool must advertise a distinct UI resource URI."""
    create_tool = await mcp_instance.get_tool("create_note")
    list_tool = await mcp_instance.get_tool("list_notes")
    get_tool = await mcp_instance.get_tool("get_note")

    create_result = await create_tool.run({"title": "A", "body": "B"})
    create_meta = create_result.meta

    list_result = await list_tool.run({})
    list_meta = list_result.meta

    get_result = await get_tool.run({"note_id": create_result.structured_content["note"]["id"]})
    get_meta = get_result.meta

    assert create_meta["ui"]["resourceUri"] != list_meta["ui"]["resourceUri"]
    assert list_meta["ui"]["resourceUri"] != get_meta["ui"]["resourceUri"]
    assert create_meta["ui"]["resourceUri"] != get_meta["ui"]["resourceUri"]


@pytest.mark.asyncio
async def test_create_note_structured_content_has_note_and_structured_content(mcp_instance):
    """create_note structured_content must contain both 'note' and 'structured_content'."""
    tool = await mcp_instance.get_tool("create_note")

    result = await tool.run({"title": "Shape", "body": "Test"})

    sc = result.structured_content
    assert isinstance(sc, dict)
    assert "note" in sc
    assert "structured_content" in sc
    assert sc["note"]["id"] == sc["structured_content"]["id"]


@pytest.mark.asyncio
async def test_list_notes_structured_content_has_count_and_notes(mcp_instance):
    """list_notes structured_content must contain 'count' and 'notes'."""
    tool = await mcp_instance.get_tool("list_notes")

    await tool.run({})

    result = await tool.run({})
    sc = result.structured_content
    assert isinstance(sc, dict)
    assert "count" in sc
    assert "notes" in sc
    assert isinstance(sc["notes"], list)
    assert isinstance(sc["count"], int)


@pytest.mark.asyncio
async def test_get_note_structured_content_has_note(mcp_instance):
    """get_note structured_content must contain 'note'."""
    create_tool = await mcp_instance.get_tool("create_note")
    get_tool = await mcp_instance.get_tool("get_note")

    create_result = await create_tool.run({"title": "Detail Shape", "body": "Test"})
    note_id = create_result.structured_content["note"]["id"]

    result = await get_tool.run({"note_id": note_id})
    sc = result.structured_content
    assert isinstance(sc, dict)
    assert "note" in sc
    assert sc["note"]["id"] == note_id
