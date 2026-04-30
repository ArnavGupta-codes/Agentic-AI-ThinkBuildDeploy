# Agentic AI in the Real World — Code Examples

Companion code for the document "Agentic AI in the Real World".
All examples use Node.js built-in modules only — no npm install required.

## Project Structure

```
mcp-server/
  server.js        Full MCP server exposing 6 tools over HTTP/JSON-RPC
  client.js        Demo client that exercises every tool
  README.md        MCP-specific notes and Claude Desktop config

agent-deployment/
  orchestrator.js  Agentic loop with tool use and retry logic
  worker.js        Priority job queue with parallel workers

agentic-ai/
  pipeline.js      4-agent research pipeline (Planner, Researcher, Writer, Critic)
  email-agent.js   Autonomous email triage agent with audit log
```

## Requirements

- Node.js 18 or higher
- No external dependencies

## Running the Examples

### MCP Server

Start the server, then run the client in a second terminal:

```
node mcp-server/server.js
node mcp-server/client.js
```

### Agent Worker Queue (no API key needed)

```
node agent-deployment/worker.js
```

### Email Triage Agent (no API key needed)

```
node agentic-ai/email-agent.js
```

### Agent Orchestrator (requires Anthropic API key)

```
ANTHROPIC_API_KEY=your_key node agent-deployment/orchestrator.js
```

### Multi-Agent Pipeline (requires Anthropic API key)

```
ANTHROPIC_API_KEY=your_key node agentic-ai/pipeline.js
```

Both the orchestrator and pipeline run in demo/mock mode automatically
when no API key is set, so you can inspect the code structure without a key.

## Connecting the MCP Server to Claude Desktop

Add to your claude_desktop_config.json:

```json
{
  "mcpServers": {
    "real-world-mcp": {
      "command": "node",
      "args": ["/path/to/mcp-server/server.js"]
    }
  }
}
```

## Connecting to the Claude API

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

## Further Reading

- MCP Specification: https://modelcontextprotocol.io
- Claude API Docs:   https://docs.anthropic.com
- MCP GitHub:        https://github.com/modelcontextprotocol
