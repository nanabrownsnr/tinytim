"""Register and serve the compiled create note UI resource."""

from pathlib import Path

from fastmcp.apps import AppConfig

CREATE_URI = "ui://tinytim/notes/create.html"
CREATE_PATH = Path(__file__).parent / "dist" / "index.html"


def load_create_html() -> str:
    """Load the compiled create note UI and explain how to create it when missing."""
    if not CREATE_PATH.is_file():
        raise RuntimeError(
            "The create note MCP App UI has not been built. Run `npm ci` and "
            "`npm run build` inside app/ui/notes/create before starting the server."
        )
    return CREATE_PATH.read_text(encoding="utf-8")


def register_resource(mcp):
    @mcp.resource(CREATE_URI, app=AppConfig())
    def create_note_view():
        """Return the bundled MCP App UI for creating notes."""
        return load_create_html()
