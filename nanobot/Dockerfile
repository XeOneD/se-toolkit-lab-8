# Single-stage build for nanobot gateway
# See wiki/dockerfile.md

FROM ${REGISTRY_PREFIX_DOCKER_HUB:-}astral/uv:python3.14-bookworm-slim AS builder

WORKDIR /app

# Copy workspace members needed for nanobot
COPY pyproject.toml uv.lock ./
COPY mcp/ ./mcp/
COPY nanobot-websocket-channel/ ./nanobot-websocket-channel/
COPY nanobot/ ./nanobot/

# Sync from nanobot directory
WORKDIR /app/nanobot
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Create non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot \
    && chown -R nonroot:nonroot /app

# Set working directory
WORKDIR /app/nanobot

# Switch to non-root user
USER nonroot:nonroot

# Expose gateway and webchat ports
EXPOSE 18790 8765

# Run the entrypoint script
CMD ["python", "/app/nanobot/entrypoint.py"]
