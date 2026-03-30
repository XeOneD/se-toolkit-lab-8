#!/usr/bin/env python3
"""Nanobot gateway entrypoint that resolves environment variables into config."""

import json
import os
import sys
from pathlib import Path


def main():
    """Resolve env vars into config and start nanobot gateway."""
    # Paths
    nanobot_dir = Path(__file__).parent
    config_path = nanobot_dir / "config.json"
    resolved_path = nanobot_dir / "config.resolved.json"
    workspace_dir = nanobot_dir / "workspace"
    
    # Load base config
    with open(config_path) as f:
        config = json.load(f)
    
    # Resolve LLM provider config from env vars
    if "LLM_API_KEY" in os.environ:
        config["providers"]["custom"]["apiKey"] = os.environ["LLM_API_KEY"]
    
    if "LLM_API_BASE_URL" in os.environ:
        config["providers"]["custom"]["apiBase"] = os.environ["LLM_API_BASE_URL"]
    
    # Resolve gateway config from env vars
    if "NANOBOT_GATEWAY_CONTAINER_ADDRESS" in os.environ:
        config.setdefault("gateway", {})["host"] = os.environ["NANOBOT_GATEWAY_CONTAINER_ADDRESS"]
    
    if "NANOBOT_GATEWAY_CONTAINER_PORT" in os.environ:
        config.setdefault("gateway", {})["port"] = int(os.environ["NANOBOT_GATEWAY_CONTAINER_PORT"])
    
    # Resolve webchat channel config from env vars
    if "NANOBOT_WEBCHAT_CONTAINER_ADDRESS" in os.environ:
        config.setdefault("channels", {}).setdefault("webchat", {})["host"] = os.environ["NANOBOT_WEBCHAT_CONTAINER_ADDRESS"]
    
    if "NANOBOT_WEBCHAT_CONTAINER_PORT" in os.environ:
        config.setdefault("channels", {}).setdefault("webchat", {})["port"] = int(os.environ["NANOBOT_WEBCHAT_CONTAINER_PORT"])
    
    # Resolve MCP server env vars
    if "mcpServers" in config.get("tools", {}):
        mcp_servers = config["tools"]["mcpServers"]
        if "lms" in mcp_servers:
            lms_config = mcp_servers["lms"]
            if "env" in lms_config:
                if "NANOBOT_LMS_BACKEND_URL" in os.environ:
                    lms_config["env"]["NANOBOT_LMS_BACKEND_URL"] = os.environ["NANOBOT_LMS_BACKEND_URL"]
                if "NANOBOT_LMS_API_KEY" in os.environ:
                    lms_config["env"]["NANOBOT_LMS_API_KEY"] = os.environ["NANOBOT_LMS_API_KEY"]
    
    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Resolved config written to {resolved_path}", file=sys.stderr)
    
    # Start nanobot gateway using the venv from builder
    nanobot_bin = "/app/.venv/bin/nanobot"
    os.execvp(nanobot_bin, [nanobot_bin, "gateway", "--config", str(resolved_path), "--workspace", str(workspace_dir)])


if __name__ == "__main__":
    main()
