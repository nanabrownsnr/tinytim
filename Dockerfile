# Builds the MCP Apps and production Python runtime. Update the UI COPY paths
# when renaming the example; generated dist/ files stay out of source control.
FROM node:22-alpine AS ui-builder

WORKDIR /ui

COPY app/ui/notes/list/package.json app/ui/notes/list/package-lock.json ./list/
COPY app/ui/notes/create/package.json app/ui/notes/create/package-lock.json ./create/
COPY app/ui/notes/detail/package.json app/ui/notes/detail/package-lock.json ./detail/

RUN cd list && npm ci --no-audit --no-fund
RUN cd create && npm ci --no-audit --no-fund
RUN cd detail && npm ci --no-audit --no-fund

COPY app/ui/notes/list/ ./list/
COPY app/ui/notes/create/ ./create/
COPY app/ui/notes/detail/ ./detail/

RUN cd list && npm run build
RUN cd create && npm run build
RUN cd detail && npm run build


FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.5.5 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    PORT=8000

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

COPY app/ ./app/
COPY --from=ui-builder /ui/list/dist/ ./app/ui/notes/list/dist/
COPY --from=ui-builder /ui/create/dist/ ./app/ui/notes/create/dist/
COPY --from=ui-builder /ui/detail/dist/ ./app/ui/notes/detail/dist/

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
