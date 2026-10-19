"""Register and serve the compiled UI resources for the notes MCP App.

Each note workflow has its own dedicated UI resource:
- LIST_URI  – ui://tinytim/notes/list.html   (list notes view)
- CREATE_URI – ui://tinytim/notes/create.html (create note view)
- DETAIL_URI – ui://tinytim/notes/detail.html (note detail view)

``VIEW_URI`` is kept for backward compatibility with existing metadata.
"""

from fastmcp.apps import AppConfig

from app.ui.notes.create.resource import (
    CREATE_PATH,
    CREATE_URI,
)
from app.ui.notes.create.resource import (
    load_create_html as _load_create_html,
)
from app.ui.notes.create.resource import (
    register_resource as _register_create_resource,
)
from app.ui.notes.detail.resource import (
    DETAIL_PATH,
    DETAIL_URI,
)
from app.ui.notes.detail.resource import (
    load_detail_html as _load_detail_html,
)
from app.ui.notes.detail.resource import (
    register_resource as _register_detail_resource,
)
from app.ui.notes.list.resource import (
    LIST_PATH,
    LIST_URI,
)
from app.ui.notes.list.resource import (
    load_list_html as _load_list_html,
)
from app.ui.notes.list.resource import (
    register_resource as _register_list_resource,
)

# Backward-compatible alias
VIEW_URI = "ui://tinytim/notes.html"
VIEW_PATH = None  # No longer a single bundled file


# ---------------------------------------------------------------------------
# Individual resource loaders
# ---------------------------------------------------------------------------


def load_list_html() -> str:
    """Load the compiled list notes UI."""
    return _load_list_html()


def load_create_html() -> str:
    """Load the compiled create note UI."""
    return _load_create_html()


def load_detail_html() -> str:
    """Load the compiled note detail UI."""
    return _load_detail_html()


def load_view_html() -> str:
    """Return the list HTML as the fallback view resource."""
    return _load_list_html()


# ---------------------------------------------------------------------------
# Resource registration
# ---------------------------------------------------------------------------


def register_resource(mcp):
    """Register all UI resources on the MCP server.

    This registers LIST_URI, CREATE_URI, and DETAIL_URI.
    VIEW_URI is registered as an alias pointing to the list view for
    backward compatibility with existing metadata.
    """
    _register_list_resource(mcp)
    _register_create_resource(mcp)
    _register_detail_resource(mcp)

    @mcp.resource(VIEW_URI, app=AppConfig())
    def notes_view():
        """Return the bundled MCP App UI for the notes feature (alias)."""
        return _load_list_html()


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    "VIEW_URI",
    "VIEW_PATH",
    "LIST_URI",
    "LIST_PATH",
    "CREATE_URI",
    "CREATE_PATH",
    "DETAIL_URI",
    "DETAIL_PATH",
    "load_list_html",
    "load_create_html",
    "load_detail_html",
    "load_view_html",
    "register_resource",
    "_register_list_resource",
    "_register_create_resource",
    "_register_detail_resource",
]
