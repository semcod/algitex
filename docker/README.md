# Docker MCP Ecosystem for Algitex

Standardized Docker images for MCP-compatible tools with multi-protocol support.

## Architecture

All tools follow a consistent pattern:

```
docker/<tool>/
├── Dockerfile           # Standardized Dockerfile with MCP SDK
└── *_mcp_server.py     # FastMCP server implementation
```

## Standardized Dockerfile Pattern

Every Dockerfile includes:

- **Python 3.11-slim** base image
- **FastMCP SDK** (`mcp[fastmcp]>=1.0.0,<2`; FastMCP was removed from MCP 2.x)
- **Multi-protocol support**: MCP stdio, MCP SSE, REST API
- **Non-root user** for security
- **Environment variables**: `TRANSPORT`, `MCP_TRANSPORT`, `PORT`

### Algitex Custom MCP Tools

| Tool | Port | Description | MCP Tools |
|------|------|-------------|-----------|
| `aider-mcp` | 3000 | AI coding assistant | `aider_ai_code`, `aider_list_models` |
| `planfile-mcp` | 8201 | Ticket/plan management | `planfile_create_ticket`, `planfile_list_tickets`, `planfile_update_ticket` |
| `vallm-mcp` | 8080 | Multi-level validation | `validate_all`, `validate_static`, `validate_runtime`, `validate_security` |
| `code2llm-mcp` | 8081 | Code analysis & Toon notation | `analyze_project`, `generate_toon`, `generate_readme` |
| `proxym-mcp` | 4000 | LLM proxy gateway | `chat_completions`, `list_models`, `budget_status` |

### Community MCP Tools from Docker Hub

| Tool | Description | Capabilities |
|------|-------------|------------|
| `mcp-github` | GitHub integration | `create_or_update_file`, `create_issue`, `create_pull_request`, `search_code` |
| `mcp-git` | Git operations | `git_status`, `git_log`, `git_diff`, `git_clone` |
| `mcp-wikipedia` | Knowledge search | `search_wikipedia`, `get_summary`, `get_content` |
| `mcp-time` | Time operations | `get_current_time`, `convert_timezone`, `parse_date` |
| `mcp-fetch` | Web scraping | `fetch_url`, `extract_content`, `fetch_metadata` |
| `mcp-filesystem` | File operations | `read_file`, `write_file`, `list_directory`, `search_files` |
| `mcp-postgres` | PostgreSQL database | `query`, `execute`, `schema_inspection` |
| `mcp-sqlite` | SQLite database | `query`, `execute`, `schema_inspection` |
| `mcp-duckduckgo` | Anonymous web search | `search`, `instant_answer` |
| `mcp-brave-search` | Brave search API | `web_search`, `image_search`, `news_search` |
| `mcp-browser` | Browser automation | `navigate`, `screenshot`, `get_content` |
| `mcp-playwright` | E2E testing | `navigate`, `screenshot`, `click`, `fill`, `evaluate` |
| `mcp-slack` | Slack integration | `send_message`, `notify`, `channel_info` |

# Using docker compose
cd docker
docker-compose up -d

# Or specific services only
docker-compose up -d aider-mcp planfile-mcp proxym
docker-compose up -d mcp-github mcp-wikipedia mcp-fetch
```

# Build a specific tool
docker build -f docker/vallm/Dockerfile -t algitex/vallm-mcp:latest .

# Run in MCP stdio mode (default)
docker run -it --rm algitex/vallm-mcp:latest

# Run in REST API mode
docker run -p 8080:8080 -e TRANSPORT=rest algitex/vallm-mcp:latest
```

# Start all MCP tools
docker compose --profile tools up -d

# Or start everything including monitoring
docker compose --profile full up -d
```

### Using MCP Tools with Claude/Cline

Configure in your MCP settings:

```json
{
  "mcpServers": {
    "vallm": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "algitex/vallm-mcp:latest"]
    },
    "code2llm": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "./:/project:ro", "algitex/code2llm-mcp:latest"]
    }
  }
}
```

# Default mode - communicates via stdin/stdout
docker run -i --rm algitex/vallm-mcp:latest
```

### REST API
```bash
docker run -p 8080:8080 -e TRANSPORT=rest algitex/vallm-mcp:latest

# Then use HTTP endpoints:
curl http://localhost:8080/health
curl -X POST http://localhost:8080/validate -d '{"path": "/project"}'
```

### MCP SSE
```bash
docker run -p 8080:8080 -e TRANSPORT=sse algitex/vallm-mcp:latest
```

## Creating New MCP Tools

1. Create directory: `docker/<tool>/`
2. Create `Dockerfile` following the standard pattern
3. Create `<tool>_mcp_server.py` using FastMCP:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-tool")

@mcp.tool()
def my_tool_function(param: str) -> dict:
    """Tool description for AI."""
    return {"result": f"Processed: {param}"}

if __name__ == "__main__":
    import os
    transport = os.getenv("TRANSPORT", "stdio")
    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        # Run REST server
        pass
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TRANSPORT` | `stdio` | Transport mode: `stdio`, `rest`, `sse` |
| `MCP_TRANSPORT` | `stdio` | MCP-specific transport setting |
| `PORT` | varies | REST API port (tool-specific) |
| `PYTHONUNBUFFERED` | `1` | Ensure Python output is not buffered |
| `ALGITEX_MCP_PROJECT_ROOT` | `/project` in project containers | Restrict project paths to the mounted workspace |
| `ALGITEX_MCP_ALLOW_MUTATION` | `false` | Allow Aider/Planfile writes for trusted clients |
| `ALGITEX_MCP_ALLOW_EXECUTE` | `false` | Allow Vallm to launch validation subprocesses |
| `ALGITEX_MCP_ALLOW_NETWORK` | `false` | Allow Proxym to make paid outbound LLM calls |
| `ALGITEX_MCP_MAX_PROMPT_BYTES` | `1048576` | Maximum aggregate prompt size for Proxym |
| `ALGITEX_MCP_MAX_OUTPUT_TOKENS` | `16384` | Maximum requested output tokens for Proxym |

Mutation, process execution, and outbound LLM access are disabled by default. Enable
only the capability needed by a trusted client, for example:

```bash
ALGITEX_MCP_ALLOW_EXECUTE=true docker compose --profile tools up vallm-mcp
```

## Health Checks

All containers expose a `/health` endpoint when running in REST mode:

```bash
curl http://localhost:<port>/health
