/**
 * Agentic AI Beyond Chatbot - Real World Example
 *
 * Multi-Agent Research Pipeline:
 *   PlannerAgent  - breaks the goal into sub-tasks
 *   ResearchAgent - gathers information for each sub-task
 *   WriterAgent   - synthesizes findings into a final report
 *   CriticAgent   - reviews and scores the output, triggers revision if needed
 *
 * Unlike a chatbot (one question, one answer), this system:
 *   - Plans autonomously
 *   - Runs research agents in parallel
 *   - Passes state between agents
 *   - Self-evaluates and iterates
 *
 * Run: ANTHROPIC_API_KEY=your_key node pipeline.js
 */

const https = require("https");

// --- Claude API --------------------------------------------------------------
async function callClaude(systemPrompt, userPrompt, jsonMode = false) {
  const apiKey = process.env.ANTHROPIC_API_KEY;

  if (!apiKey || apiKey === "YOUR_KEY") {
    // Return a mock response when no API key is available (demo mode)
    return mockAgentResponse(systemPrompt, userPrompt);
  }

  const body = JSON.stringify({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1024,
    system: systemPrompt + (jsonMode ? "\n\nAlways respond with valid JSON only. No explanation." : ""),
    messages: [{ role: "user", content: userPrompt }],
  });

  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        hostname: "api.anthropic.com",
        path: "/v1/messages",
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "anthropic-version": "2023-06-01",
          "x-api-key": apiKey,
        },
      },
      (res) => {
        let data = "";
        res.on("data", (c) => (data += c));
        res.on("end", () => {
          const parsed = JSON.parse(data);
          const text = parsed.content?.[0]?.text || "";
          if (jsonMode) {
            try { resolve(JSON.parse(text)); }
            catch { resolve({ raw: text }); }
          } else {
            resolve(text);
          }
        });
      }
    );
    req.on("error", reject);
    req.write(body);
    req.end();
  });
}

// --- Mock Responses (demo mode, no API key needed) ---------------------------
function mockAgentResponse(system, prompt) {
  if (system.includes("Planner")) {
    return Promise.resolve({
      goal: prompt,
      subtasks: [
        { id: 1, title: "Define the problem scope", assignTo: "ResearchAgent" },
        { id: 2, title: "Gather relevant data and examples", assignTo: "ResearchAgent" },
        { id: 3, title: "Identify key insights and patterns", assignTo: "ResearchAgent" },
        { id: 4, title: "Synthesize findings into a coherent report", assignTo: "WriterAgent" },
      ],
    });
  }
  if (system.includes("Researcher")) {
    return Promise.resolve(
      "Research findings for: \"" + prompt + "\"\n\n" +
      "Key points identified:\n" +
      "1. Multiple real-world applications exist across industries\n" +
      "2. Best practices have emerged from industry experience\n" +
      "3. Common challenges include scaling and reliability\n" +
      "4. The tooling ecosystem is rapidly evolving"
    );
  }
  if (system.includes("Writer")) {
    return Promise.resolve(
      "# Report\n\n" +
      "Based on the research conducted, this topic encompasses several important dimensions.\n\n" +
      "The findings indicate strong adoption across industries with continued growth expected. " +
      "Implementation requires careful consideration of architecture, tooling, and team readiness.\n\n" +
      "## Key Recommendations\n" +
      "1. Start with a focused pilot project\n" +
      "2. Invest in observability from day one\n" +
      "3. Build iteratively, measure results"
    );
  }
  if (system.includes("Critic")) {
    return Promise.resolve({
      score: 8,
      feedback: "Good structure and coverage. Could benefit from more concrete examples and metrics.",
      approved: true,
    });
  }
  return Promise.resolve("Mock response");
}

// --- Agents ------------------------------------------------------------------

class PlannerAgent {
  async plan(goal) {
    console.log('\nPlannerAgent: Planning for goal: "' + goal + '"');
    const result = await callClaude(
      'You are a Planner Agent. Given a high-level goal, break it into 3-5 concrete sub-tasks. ' +
      'Respond with JSON: { "goal": "...", "subtasks": [{ "id": 1, "title": "...", "assignTo": "ResearchAgent|WriterAgent" }] }',
      goal,
      true
    );
    console.log("   Plan created with " + (result.subtasks?.length || 0) + " sub-tasks");
    return result;
  }
}

class ResearchAgent {
  async research(subtask) {
    console.log('\nResearchAgent: Researching "' + subtask.title + '"');
    const result = await callClaude(
      "You are a Research Agent. Gather information and insights on a specific topic. " +
      "Be concise but thorough. Provide factual, practical information.",
      "Research task: " + subtask.title + "\n\nProvide 3-5 key insights relevant to this topic."
    );
    console.log("   Research complete (" + result.length + " chars)");
    return { subtask, findings: result };
  }
}

class WriterAgent {
  async write(goal, researchResults) {
    console.log("\nWriterAgent: Synthesizing findings into report");
    const context = researchResults
      .map((r, i) => "## Section " + (i + 1) + ": " + r.subtask.title + "\n" + r.findings)
      .join("\n\n");
    const result = await callClaude(
      "You are a Writer Agent. Synthesize research findings into a coherent, well-structured report. " +
      "Use clear headings, maintain professional tone, and include actionable recommendations.",
      "Goal: " + goal + "\n\nResearch findings:\n\n" + context + "\n\nWrite a complete report."
    );
    console.log("   Report written (" + result.length + " chars)");
    return result;
  }
}

class CriticAgent {
  async review(report) {
    console.log("\nCriticAgent: Reviewing report quality");
    const result = await callClaude(
      'You are a Critic Agent. Review reports for quality, accuracy, and usefulness. ' +
      'Respond with JSON: { "score": 1-10, "feedback": "...", "approved": true|false }',
      "Review this report:\n\n" + report.slice(0, 800),
      true
    );
    console.log("   Score: " + result.score + "/10 | Approved: " + result.approved);
    return result;
  }
}

// --- Pipeline Orchestrator ---------------------------------------------------
class AgenticPipeline {
  constructor() {
    this.planner = new PlannerAgent();
    this.researcher = new ResearchAgent();
    this.writer = new WriterAgent();
    this.critic = new CriticAgent();
    this.state = {};
  }

  async run(goal) {
    const startTime = Date.now();
    console.log("=".repeat(60));
    console.log("AGENTIC PIPELINE STARTING");
    console.log("Goal: " + goal);
    console.log("=".repeat(60));

    // Stage 1: Planning
    const plan = await this.planner.plan(goal);
    this.state.plan = plan;

    // Stage 2: Research (run in parallel)
    console.log("\nRunning " + plan.subtasks.length + " research tasks in parallel...");
    const researchTasks = plan.subtasks
      .filter((t) => t.assignTo === "ResearchAgent")
      .map((t) => this.researcher.research(t));
    const researchResults = await Promise.all(researchTasks);
    this.state.research = researchResults;

    // Stage 3: Writing
    const report = await this.writer.write(goal, researchResults);
    this.state.report = report;

    // Stage 4: Critique with optional revision
    let review = await this.critic.review(report);
    this.state.review = review;

    if (!review.approved && review.score < 6) {
      console.log("\nReport quality below threshold. Requesting revision...");
      const revised = await this.writer.write(
        goal + "\n\nPrevious feedback: " + review.feedback,
        researchResults
      );
      this.state.report = revised;
      review = await this.critic.review(revised);
      this.state.review = review;
    }

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

    console.log("\n" + "=".repeat(60));
    console.log("PIPELINE COMPLETE");
    console.log("Duration: " + elapsed + "s");
    console.log("Quality score: " + review.score + "/10");
    console.log("Feedback: " + review.feedback);
    console.log("=".repeat(60));
    console.log("\nFINAL REPORT:\n");
    console.log(this.state.report);

    return this.state;
  }
}

// --- Main --------------------------------------------------------------------
async function main() {
  const pipeline = new AgenticPipeline();
  await pipeline.run(
    "Explain the real-world applications and deployment strategies for agentic AI systems in enterprise environments"
  );
}

main().catch(console.error);
