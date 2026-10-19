# Tinytim MCP Server

A production-shaped [FastMCP](https://gofastmcp.com/) server with embedded
[MCP Apps](https://modelcontextprotocol.io/extensions/apps/overview) for
managing notes.

## Architecture
- **app/config.py** -- Pydantic settings, logging setup, MCP name
- **app/main.py** -- ASGI app composition, tool/resource/route registration
- **app/auth.py** -- JWT verifier for MCP requests
- **app/twynity.py** -- Public manifest and health routes
- **app/tools/notes.py** -- `create_note`, `list_notes`, `get_note` tools
- **app/ui/notes/** -- React UIs built with Vite, served as MCP resources
  - **list/** -- List notes view (`ui://tinytim/notes/list.html`)
  - **create/** -- Create note view (`ui://tinytim/notes/create.html`)
  - **detail/** -- Note detail view (`ui://tinytim/notes/detail.html`)

## Tools
### create_note -- title, body, optional tags
### list_notes -- all notes
### get_note -- by id

Each tool advertises its own dedicated UI resource URI so MCP clients can
render the most appropriate interface for the operation.

## UI Resource URIs
| Tool        | UI Resource URI                                |
|-------------|------------------------------------------------|
| create_note | `ui://tinytim/notes/create.html`                |
| list_notes  | `ui://tinytim/notes/list.html`                  |
| get_note    | `ui://tinytim/notes/detail.html`                |

## Local development
```bash
uv sync
cd app/ui/notes/list && npm ci && npm run build && cd ../..
cd app/ui/notes/create && npm ci && npm run build && cd ../..
cd app/ui/notes/detail && npm ci && npm run build && cd ../..
uv run python -m app.main
```

## Endpoints
| Route | Description |
|-------|-------------|
| `/api/v1/health` | Public health check |
| `/api/v1/.well-known/mcp.json` | Public manifest |
| `/mcp` | MCP Streamable HTTP transport |
