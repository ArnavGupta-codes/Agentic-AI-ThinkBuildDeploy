/**
 * MCP Client - test script to talk to the MCP server
 *
 * Run: node client.js
 * (Make sure server.js is running first: node server.js)
 */

const http = require("http");

let msgId = 1;

function rpc(method, params = {}) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ jsonrpc: "2.0", id: msgId++, method, params });
    const req = http.request(
      {
        hostname: "localhost",
        port: 3000,
        path: "/mcp",
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Content-Length": Buffer.byteLength(body),
        },
      },
      (res) => {
        let data = "";
        res.on("data", (c) => (data += c));
        res.on("end", () => resolve(JSON.parse(data)));
      }
    );
    req.on("error", reject);
    req.write(body);
    req.end();
  });
}

async function main() {
  console.log("=== MCP Client Demo ===\n");

  // 1. Initialize handshake
  const init = await rpc("initialize", {
    protocolVersion: "2024-11-05",
    clientInfo: { name: "demo-client" },
  });
  console.log("Initialized:", init.result.serverInfo);

  // 2. List available tools
  const tools = await rpc("tools/list");
  console.log("\nAvailable tools:", tools.result.tools.map((t) => t.name));

  // 3. Call get_system_info
  const sysinfo = await rpc("tools/call", { name: "get_system_info", arguments: {} });
  console.log("\nSystem info:", JSON.parse(sysinfo.result.content[0].text));

  // 4. Query the in-memory database
  const dbResult = await rpc("tools/call", {
    name: "query_database",
    arguments: { sql: "SELECT * FROM users" },
  });
  console.log("\nDB users:", JSON.parse(dbResult.result.content[0].text));

  // 5. Write then read back a file
  await rpc("tools/call", {
    name: "write_file",
    arguments: {
      path: "/tmp/mcp-test.txt",
      content: "Hello from MCP!\nWritten at: " + new Date().toISOString(),
    },
  });
  const fileResult = await rpc("tools/call", {
    name: "read_file",
    arguments: { path: "/tmp/mcp-test.txt" },
  });
  console.log("\nFile read:", JSON.parse(fileResult.result.content[0].text));

  console.log("\nAll demos complete.");
}

main().catch(console.error);
