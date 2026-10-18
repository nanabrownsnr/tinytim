"""Notes management tools with MCP App UI integration.

Provides create_note, list_notes, and get_note. All tools share a stable
``ui://tinytim/notes.html`` URI that links to the compiled React UI.
"""

import threading
import uuid
from datetime import UTC, datetime
from typing import Any

from fastmcp.apps import AppConfig
from fastmcp.tools import ToolResult

from app.ui.notes.resource import VIEW_URI

# Module-level state: in-memory notes store shared across all tool calls.
_notes_lock = threading.Lock()
_notes_store: dict[str, dict[str, Any]] = {}


def _create_note_entry(title: str, body: str, tags: list[str] | None) -> dict[str, Any]:
    note_id = uuid.uuid4().hex
    now = datetime.now(UTC).isoformat()
    return {
        "id": note_id,
        "title": title,
        "body": body,
        "tags": tags or [],
        "created_at": now,
        "status": "created",
    }


def _get_all_notes() -> list[dict[str, Any]]:
    with _notes_lock:
        return list(_notes_store.values())


def _get_note(note_id: str) -> dict[str, Any] | None:
    with _notes_lock:
        return _notes_store.get(note_id)


def _add_note(entry: dict[str, Any]) -> dict[str, Any]:
    with _notes_lock:
        _notes_store[entry["id"]] = entry
    return entry


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------


def _make_meta() -> dict[str, Any]:
    return {
        "ui": {"resourceUri": VIEW_URI, "visibility": ["model", "app"]},
        "ui/resourceUri": VIEW_URI,
    }


def register_tool(mcp):
    @mcp.tool(
        app=AppConfig(
            resource_uri=VIEW_URI,
            visibility=["model", "app"],
        )
    )
    def create_note(
        title: str,
        body: str,
        tags: list[str] | None = None,
    ) -> ToolResult:
        """Create a new note with the given title and body.

        Args:
            title: The note title. Must be non-empty after trimming whitespace.
            body: The note body content. Must be non-empty after trimming whitespace.
            tags: Optional list of tag strings for categorising the note.

        Returns:
            A ToolResult containing the created note data in structured_content
            along with a short text content for the model.

        Raises:
            ValueError: If ``title`` or ``body`` is empty after trimming.
        """
        clean_title = title.strip()
        clean_body = body.strip()

        if not clean_title:
            raise ValueError("title must be a non-empty string")
        if not clean_body:
            raise ValueError("body must be a non-empty string")

        entry = _create_note_entry(clean_title, clean_body, tags)
        _add_note(entry)

        structured: dict[str, Any] = {
            "note": entry,
            "structured_content": entry,
        }

        return ToolResult(
            content=f'Note "{entry["title"]}" created successfully.',
            structured_content=structured,
            meta=_make_meta(),
        )

    @mcp.tool()
    def list_notes() -> ToolResult:
        """List all notes created during the running process.

        Returns:
            A ToolResult with structured_content containing ``count`` and
            ``notes`` (a list of note objects).
        """
        notes = _get_all_notes()
        structured: dict[str, Any] = {
            "count": len(notes),
            "notes": notes,
        }
        return ToolResult(
            content=f"{len(notes)} note(s) found.",
            structured_content=structured,
            meta=_make_meta(),
        )

    @mcp.tool()
    def get_note(note_id: str) -> ToolResult:
        """Retrieve a single note by its id.

        Args:
            note_id: The unique identifier of the note to retrieve.

        Returns:
            A ToolResult with the note in structured_content.

        Raises:
            ValueError: If no note with the given id exists.
        """
        note = _get_note(note_id)
        if note is None:
            raise ValueError(f"Note not found: {note_id}")

        structured: dict[str, Any] = {"note": note}
        return ToolResult(
            content=note["title"],
            structured_content=structured,
            meta=_make_meta(),
        )
