"""Register and serve the compiled note detail UI resource."""

from pathlib import Path

from fastmcp.apps import AppConfig

DETAIL_URI = "ui://tinytim/notes/detail.html"
DETAIL_PATH = Path(__file__).parent / "dist" / "index.html"


def load_detail_html() -> str:
    """Load the compiled note detail UI and explain how to create it when missing."""
    if not DETAIL_PATH.is_file():
        raise RuntimeError(
            "The note detail MCP App UI has not been built. Run `npm ci` and "
            "`npm run build` inside app/ui/notes/detail before starting the server."
        )
    return DETAIL_PATH.read_text(encoding="utf-8")


def register_resource(mcp):
    @mcp.resource(DETAIL_URI, app=AppConfig())
    def note_detail_view():
        """Return the bundled MCP App UI for viewing a note detail."""
        return load_detail_html()
