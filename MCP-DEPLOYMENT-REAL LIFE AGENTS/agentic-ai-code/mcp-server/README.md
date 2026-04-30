# MCP Server — Real World Example

## What is MCP?
Model Context Protocol (MCP) is an open standard by Anthropic that lets AI models (like Claude) connect to external tools, databases, APIs, and file systems through a unified JSON-RPC protocol.

## Architecture

```
┌─────────────────────┐        HTTP/JSON-RPC        ┌──────────────────┐
│   Claude / AI Agent │ ◄──────────────────────────► │   MCP Server     │
│   (MCP Client)      │      POST /mcp               │   (This Server)  │
└─────────────────────┘                              └──────────────────┘
                                                              │
                                          ┌───────────────────┼───────────────┐
                                          ▼                   ▼               ▼
                                     Filesystem          In-Memory DB     HTTP Fetch
```

## Tools Exposed

| Tool | Description |
|------|-------------|
| `read_file` | Read a local file |
| `write_file` | Write content to a file |
| `list_directory` | List files in a directory |
| `query_database` | Run SQL against in-memory DB |
| `fetch_url` | Fetch a public URL |
| `get_system_info` | Return server environment info |

## Quick Start

```bash
node server.js          # Start the MCP server on port 3000
node client.js          # Run the demo client
```

## Connecting to Claude API

```javascript
const response = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1000,
    messages: [{ role: "user", content: "List the users in the database" }],
    mcp_servers: [{
      type: "url",
      url: "http://localhost:3000/mcp",
      name: "my-mcp-server"
    }]
  })
});
```

## Real-World Use Cases
- Connect Claude to your company's internal database
- Let AI read/write project files
- Expose APIs as tools without prompt engineering
- Build multi-agent pipelines with shared tool access
