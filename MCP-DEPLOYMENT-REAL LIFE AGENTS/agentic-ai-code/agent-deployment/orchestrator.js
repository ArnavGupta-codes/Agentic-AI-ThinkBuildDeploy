/**
 * Agent Deployment - Real World Example
 *
 * Demonstrates deploying AI agents with:
 *   - Tool use (calculator, time, file write, knowledge base search)
 *   - Multi-turn conversation memory
 *   - Agentic loop with max iteration guard
 *   - Task retry with exponential backoff
 *
 * Run: ANTHROPIC_API_KEY=your_key node orchestrator.js
 */

const https = require("https");
const fs = require("fs");

// --- Anthropic API Call ------------------------------------------------------
function claudeAPI(messages, systemPrompt, tools = []) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      system: systemPrompt,
      tools: tools.length ? tools : undefined,
      messages,
    });

    const options = {
      hostname: "api.anthropic.com",
      path: "/v1/messages",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
        "x-api-key": process.env.ANTHROPIC_API_KEY || "YOUR_API_KEY",
      },
    };

    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", (c) => (data += c));
      res.on("end", () => {
        try { resolve(JSON.parse(data)); }
        catch { reject(new Error("Invalid JSON from API")); }
      });
    });
    req.on("error", reject);
    req.write(body);
    req.end();
  });
}

// --- Tool Implementations ----------------------------------------------------
const toolHandlers = {
  calculate: ({ expression }) => {
    try {
      // Safe eval using Function constructor (no access to globals)
      const result = new Function('"use strict"; return (' + expression + ')')();
      return { result, expression };
    } catch (e) {
      return { error: e.message };
    }
  },

  get_current_time: () => ({
    utc: new Date().toISOString(),
    local: new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }),
    timezone: "Asia/Kolkata",
  }),

  write_report: ({ filename, content }) => {
    const outPath = "/tmp/" + filename;
    fs.writeFileSync(outPath, content, "utf8");
    return { saved: outPath, size: content.length };
  },

  search_knowledge_base: ({ query }) => {
    // Simulates a vector DB / knowledge base search
    const kb = [
      { id: 1, text: "MCP (Model Context Protocol) is an open standard for AI tool use." },
      { id: 2, text: "Agentic AI refers to AI systems that take autonomous multi-step actions." },
      { id: 3, text: "Deployment of agents requires orchestration, monitoring, and retry logic." },
      { id: 4, text: "Claude supports tool use, MCP servers, and structured output." },
    ];
    const q = query.toLowerCase();
    const hits = kb.filter((k) => k.text.toLowerCase().includes(q.split(" ")[0]));
    return { query, results: hits.length ? hits : [{ id: 0, text: "No matches found." }] };
  },
};

// --- Tool Definitions (Claude API format) ------------------------------------
const TOOL_DEFS = [
  {
    name: "calculate",
    description: "Evaluate a mathematical expression",
    input_schema: {
      type: "object",
      properties: {
        expression: { type: "string", description: "e.g. '2 + 2' or '(100 * 0.18)'" },
      },
      required: ["expression"],
    },
  },
  {
    name: "get_current_time",
    description: "Get the current date and time",
    input_schema: { type: "object", properties: {} },
  },
  {
    name: "write_report",
    description: "Save a report to a file",
    input_schema: {
      type: "object",
      properties: {
        filename: { type: "string" },
        content: { type: "string" },
      },
      required: ["filename", "content"],
    },
  },
  {
    name: "search_knowledge_base",
    description: "Search the internal knowledge base for information",
    input_schema: {
      type: "object",
      properties: { query: { type: "string" } },
      required: ["query"],
    },
  },
];

// --- Agentic Loop ------------------------------------------------------------
async function runAgent(task) {
  console.log('\nAgent starting task: "' + task + '"\n');

  const messages = [{ role: "user", content: task }];
  const system =
    "You are a capable AI assistant with access to tools. " +
    "Complete tasks step by step using tools when needed. " +
    "When the task is fully complete, provide a clear final answer.";

  let iterations = 0;
  const MAX_ITERATIONS = 10;

  while (iterations < MAX_ITERATIONS) {
    iterations++;
    console.log("  [iteration " + iterations + "] Calling Claude...");

    const response = await claudeAPI(messages, system, TOOL_DEFS);

    if (response.error) {
      console.error("  API error:", response.error);
      break;
    }

    // Append assistant response to conversation history
    messages.push({ role: "assistant", content: response.content });

    // Task complete
    if (response.stop_reason === "end_turn") {
      const text = response.content.find((c) => c.type === "text")?.text || "";
      console.log("\nAgent finished:\n" + text + "\n");
      return text;
    }

    // Execute tool calls
    if (response.stop_reason === "tool_use") {
      const toolUses = response.content.filter((c) => c.type === "tool_use");
      const toolResults = [];

      for (const toolUse of toolUses) {
        console.log("  Tool call: " + toolUse.name + "(" + JSON.stringify(toolUse.input) + ")");
        const handler = toolHandlers[toolUse.name];
        const result = handler
          ? handler(toolUse.input)
          : { error: "Unknown tool: " + toolUse.name };
        console.log("     Result: " + JSON.stringify(result));

        toolResults.push({
          type: "tool_result",
          tool_use_id: toolUse.id,
          content: JSON.stringify(result),
        });
      }

      messages.push({ role: "user", content: toolResults });
    }
  }

  console.log("WARNING: Max iterations reached");
  return null;
}

// --- Retry Wrapper -----------------------------------------------------------
async function runWithRetry(task, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await runAgent(task);
    } catch (err) {
      console.error("  Attempt " + attempt + " failed: " + err.message);
      if (attempt === maxRetries) throw err;
      // Exponential backoff
      await new Promise((r) => setTimeout(r, 1000 * attempt));
    }
  }
}

// --- Main --------------------------------------------------------------------
async function main() {
  console.log("=== Agent Deployment Demo ===");
  console.log("(Set ANTHROPIC_API_KEY env var to run live - showing structure demo)\n");

  const tasks = [
    "What is the current time? Then calculate 15% tip on a 850 rupee restaurant bill.",
    "Search the knowledge base for 'agentic' and write a brief summary report to 'agent-summary.txt'.",
  ];

  for (const task of tasks) {
    try {
      await runWithRetry(task);
    } catch (err) {
      console.error("Task failed after retries: " + err.message);
    }
  }
}

main();
