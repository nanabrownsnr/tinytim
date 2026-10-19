"""Register and serve the compiled list notes UI resource."""

from pathlib import Path

from fastmcp.apps import AppConfig

LIST_URI = "ui://tinytim/notes/list.html"
LIST_PATH = Path(__file__).parent / "dist" / "index.html"


def load_list_html() -> str:
    """Load the compiled list notes UI and explain how to create it when missing."""
    if not LIST_PATH.is_file():
        raise RuntimeError(
            "The list notes MCP App UI has not been built. Run `npm ci` and "
            "`npm run build` inside app/ui/notes/list before starting the server."
        )
    return LIST_PATH.read_text(encoding="utf-8")


def register_resource(mcp):
    @mcp.resource(LIST_URI, app=AppConfig())
    def list_notes_view():
        """Return the bundled MCP App UI for listing notes."""
        return load_list_html()
