"""Register and serve the compiled UI resource for the notes app.

Change ``VIEW_URI`` with the matching value in the tools, and update
``VIEW_PATH`` only if you change the frontend build output location.
"""

from pathlib import Path

from fastmcp.apps import AppConfig

VIEW_URI = "ui://tinytim/notes.html"
VIEW_PATH = Path(__file__).parent / "dist" / "index.html"


def load_view_html() -> str:
    """Load the compiled UI and explain how to create it when it is missing."""
    if not VIEW_PATH.is_file():
        raise RuntimeError(
            "The MCP App UI has not been built. Run `npm ci` and "
            "`npm run build` inside app/ui/notes before starting the server."
        )
    return VIEW_PATH.read_text(encoding="utf-8")


def register_resource(mcp):
    @mcp.resource(VIEW_URI, app=AppConfig())
    def notes_view():
        """Return the bundled MCP App UI for the notes feature."""
        return load_view_html()
