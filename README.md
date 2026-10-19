# Tinytim MCP Server

A production-shaped [FastMCP](https://gofastmcp.com/) server with an embedded
[MCP App](https://modelcontextprotocol.io/extensions/apps/overview) for
managing notes.

## Example output

Calling `create_note` creates a note and links to the MCP App UI. The notes
app shows a sidebar list, selected note details, and a creation form.

## Architecture

The project follows the Twynity MCP basic template structure:

- **`app/config.py`** – Pydantic settings, logging setup, MCP name
- **`app/main.py`** – ASGI app composition, tool/resource/route registration
- **`app/auth.py`** – JWT verifier for MCP requests
- **`app/twynity.py`** – Public manifest and health routes
- **`app/tools/notes.py`** – `create_note`, `list_notes`, `get_note` tools
- **`app/ui/notes/`** – React UI built with Vite, served as an MCP resource

## Tools

### `create_note`

Creates a note with a title and body. Optional `tags` list for categorisation.

```
create_note(title="Meeting Notes", body="Discussed roadmap", tags=["work", "meeting"])
```

### `list_notes`

Returns all notes created during the running process.

```
list_notes()
```

### `get_note`

Retrieves a single note by its id.

```
get_note(note_id="<id>")
```

## Local development

```bash
# Install Python dependencies
uv sync

# Build the UI
cd app/ui/notes && npm ci && npm run build && cd ../../..

# Run the server
uv run python -m app.main
```

The server starts on `0.0.0.0:8000`.

## Docker

```bash
docker compose build
docker compose up
```

Health check is available at `http://localhost:8000/api/v1/health`.

## Endpoints

| Route | Description |
|-------|-------------|
| `/api/v1/health` | Public health check – returns `{"status": "ok"}` |
| `/api/v1/.well-known/mcp.json` | Public manifest – returns name and version |
| `/mcp` | MCP Streamable HTTP transport |

## Project structure

```
pyproject.toml
Dockerfile
docker-compose.yml
app/
  config.py
  main.py
  auth.py
  twynity.py
  tools/
    notes.py
  ui/
    notes/
      resource.py
      index.html
      package.json
      vite.config.js
      src/
        App.jsx
        main.jsx
        style.css
tests/
  conftest.py
  pytest.ini
  test_tools.py
  test_resources.py
  test_twynity.py
  test_startup.py
```
