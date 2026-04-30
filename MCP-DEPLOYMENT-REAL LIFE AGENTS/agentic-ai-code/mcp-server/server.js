/**
 * MCP Server - Real World Example
 * A Model Context Protocol server that exposes tools to AI agents.
 * Demonstrates: file system tools, web fetch, database query simulation.
 *
 * Run: node server.js
 * Connect via: Claude Desktop, Claude API (mcp_servers param), or any MCP client
 */

const http = require("http");
const fs = require("fs");
const path = require("path");

// --- MCP Protocol Constants --------------------------------------------------
const PROTOCOL_VERSION = "2024-11-05";
const SERVER_NAME = "real-world-mcp-server";
const SERVER_VERSION = "1.0.0";

// --- Tool Definitions --------------------------------------------------------
const TOOLS = [
  {
    name: "read_file",
    description: "Read the contents of a file from the local filesystem",
    inputSchema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Absolute or relative path to the file" },
      },
      required: ["path"],
    },
  },
  {
    name: "write_file",
    description: "Write content to a file on the local filesystem",
    inputSchema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Path to the file to write" },
        content: { type: "string", description: "Content to write into the file" },
      },
      required: ["path", "content"],
    },
  },
  {
    name: "list_directory",
    description: "List files and directories at a given path",
    inputSchema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Directory path to list" },
      },
      required: ["path"],
    },
  },
  {
    name: "query_database",
    description: "Run a simulated SQL query against the in-memory database",
    inputSchema: {
      type: "object",
      properties: {
        sql: { type: "string", description: "SQL SELECT statement" },
      },
      required: ["sql"],
    },
  },
  {
    name: "fetch_url",
    description: "Fetch the text content of a public URL",
    inputSchema: {
      type: "object",
      properties: {
        url: { type: "string", description: "URL to fetch" },
      },
      required: ["url"],
    },
  },
  {
    name: "get_system_info",
    description: "Return basic info about the server environment",
    inputSchema: { type: "object", properties: {} },
  },
];

// --- In-Memory Database ------------------------------------------------------
const DB = {
  users: [
    { id: 1, name: "Alice Sharma", email: "alice@example.com", role: "admin" },
    { id: 2, name: "Bob Patel", email: "bob@example.com", role: "editor" },
    { id: 3, name: "Carol Nair", email: "carol@example.com", role: "viewer" },
  ],
  orders: [
    { id: 101, user_id: 1, product: "MCP License", amount: 299, status: "completed" },
    { id: 102, user_id: 2, product: "Agent SDK", amount: 99, status: "pending" },
    { id: 103, user_id: 1, product: "Cloud Plan", amount: 49, status: "completed" },
  ],
};

function queryDB(sql) {
  const match = sql.match(/FROM\s+(\w+)/i);
  if (!match) return { error: "Could not parse table name from SQL" };
  const table = match[1].toLowerCase();
  if (!DB[table]) return { error: "Table '" + table + "' not found. Available: " + Object.keys(DB).join(", ") };
  return { rows: DB[table], count: DB[table].length };
}

// --- Tool Executor -----------------------------------------------------------
async function executeTool(name, args) {
  switch (name) {
    case "read_file": {
      const filePath = path.resolve(args.path);
      if (!fs.existsSync(filePath)) return { error: "File not found: " + filePath };
      const content = fs.readFileSync(filePath, "utf8");
      return { content, size: content.length, path: filePath };
    }
    case "write_file": {
      const filePath = path.resolve(args.path);
      fs.mkdirSync(path.dirname(filePath), { recursive: true });
      fs.writeFileSync(filePath, args.content, "utf8");
      return { success: true, path: filePath, bytesWritten: args.content.length };
    }
    case "list_directory": {
      const dirPath = path.resolve(args.path);
      if (!fs.existsSync(dirPath)) return { error: "Directory not found: " + dirPath };
      const entries = fs.readdirSync(dirPath, { withFileTypes: true });
      return {
        path: dirPath,
        entries: entries.map((e) => ({ name: e.name, type: e.isDirectory() ? "dir" : "file" })),
      };
    }
    case "query_database": {
      return queryDB(args.sql);
    }
    case "fetch_url": {
      return new Promise((resolve) => {
        const lib = args.url.startsWith("https") ? require("https") : require("http");
        lib
          .get(args.url, (res) => {
            let data = "";
            res.on("data", (chunk) => (data += chunk));
            res.on("end", () => resolve({ status: res.statusCode, body: data.slice(0, 2000) }));
          })
          .on("error", (err) => resolve({ error: err.message }));
      });
    }
    case "get_system_info": {
      return {
        platform: process.platform,
        node: process.version,
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        cwd: process.cwd(),
      };
    }
    default:
      return { error: "Unknown tool: " + name };
  }
}

// --- JSON-RPC Handler --------------------------------------------------------
async function handleRequest(body) {
  let req;
  try {
    req = JSON.parse(body);
  } catch {
    return { jsonrpc: "2.0", error: { code: -32700, message: "Parse error" }, id: null };
  }

  const { id, method, params } = req;

  switch (method) {
    case "initialize":
      return {
        jsonrpc: "2.0",
        id,
        result: {
          protocolVersion: PROTOCOL_VERSION,
          capabilities: { tools: {} },
          serverInfo: { name: SERVER_NAME, version: SERVER_VERSION },
        },
      };

    case "tools/list":
      return { jsonrpc: "2.0", id, result: { tools: TOOLS } };

    case "tools/call": {
      const { name, arguments: args } = params;
      const result = await executeTool(name, args || {});
      return {
        jsonrpc: "2.0",
        id,
        result: {
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          isError: !!result.error,
        },
      };
    }

    case "notifications/initialized":
      return null; // notification - no response needed

    default:
      return { jsonrpc: "2.0", error: { code: -32601, message: "Method not found: " + method }, id };
  }
}

// --- HTTP Server -------------------------------------------------------------
const PORT = process.env.PORT || 3000;

const server = http.createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.method !== "POST" || req.url !== "/mcp") {
    res.writeHead(404);
    res.end(JSON.stringify({ error: "Not found. POST to /mcp" }));
    return;
  }

  let body = "";
  req.on("data", (chunk) => (body += chunk));
  req.on("end", async () => {
    const response = await handleRequest(body);
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(response ? JSON.stringify(response) : "");
  });
});

server.listen(PORT, () => {
  console.log("MCP Server running at http://localhost:" + PORT + "/mcp");
  console.log("Tools available: " + TOOLS.map((t) => t.name).join(", "));
  console.log("Protocol version: " + PROTOCOL_VERSION);
});
