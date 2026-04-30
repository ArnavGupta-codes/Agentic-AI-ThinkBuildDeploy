/**
 * Agentic AI - Autonomous Email Triage Agent
 *
 * This agent monitors a simulated inbox and autonomously:
 *   1. Reads and classifies each email
 *   2. Decides an action: reply, escalate, archive, or create task
 *   3. Takes the action without human intervention
 *   4. Logs every decision for audit and compliance
 *
 * This is the core pattern behind: AI customer support, inbox zero tools,
 * automated helpdesks, and business process automation.
 *
 * Run: node email-agent.js
 */

// --- Simulated Email Inbox ---------------------------------------------------
const INBOX = [
  {
    id: "e001",
    from: "urgent@client.com",
    subject: "URGENT: Production server is down!!",
    body: "Our production environment has been down for 30 minutes. We are losing revenue. Please fix ASAP.",
    timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
  },
  {
    id: "e002",
    from: "hr@company.com",
    subject: "Team offsite dates confirmation",
    body: "Hi, can you confirm your availability for the team offsite: March 15-17?",
    timestamp: new Date(Date.now() - 20 * 60000).toISOString(),
  },
  {
    id: "e003",
    from: "newsletter@techdigest.io",
    subject: "This week in AI: GPT-5, Gemini Ultra, and more",
    body: "Read about the latest in AI research and industry news...",
    timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
  },
  {
    id: "e004",
    from: "billing@saasprovider.com",
    subject: "Invoice #INV-2026-0412 - Payment Due",
    body: "Your invoice of $1,299 is due on April 20, 2026. Please login to pay.",
    timestamp: new Date(Date.now() - 2 * 60 * 60000).toISOString(),
  },
  {
    id: "e005",
    from: "candidate@applicant.com",
    subject: "Job application: Senior Backend Engineer",
    body: "Hello, I am applying for the Senior Backend Engineer position. I have 8 years of experience...",
    timestamp: new Date(Date.now() - 3 * 60 * 60000).toISOString(),
  },
];

// --- Action Handlers ---------------------------------------------------------
const actionHandlers = {
  reply: (email, draft) => {
    console.log("     Sending reply to " + email.from + ":");
    console.log('        "' + draft.slice(0, 120) + '..."');
    return { sent: true, to: email.from, preview: draft.slice(0, 120) };
  },

  escalate: (email, reason) => {
    console.log("     ESCALATING to on-call team:");
    console.log("        Reason: " + reason);
    console.log("        Email from: " + email.from + " | Subject: " + email.subject);
    return { escalated: true, reason, notified: ["on-call@company.com", "manager@company.com"] };
  },

  archive: (email, label) => {
    console.log('     Archiving with label: "' + label + '"');
    return { archived: true, label };
  },

  create_task: (email, task) => {
    console.log("     Creating task in project tracker:");
    console.log('        "' + task + '"');
    return { taskCreated: true, title: task, assignedTo: "team@company.com" };
  },
};

// --- Email Classifier --------------------------------------------------------
// Rule-based in this demo. In production, replace with a Claude API call
// for more accurate classification on real-world email variety.
function classifyEmail(email) {
  const subject = email.subject.toLowerCase();
  const body = email.body.toLowerCase();

  if (subject.includes("urgent") || subject.includes("down") || body.includes("production")) {
    return {
      category: "incident",
      priority: "critical",
      action: "escalate",
      reasoning: "Production incident detected - immediate escalation required",
      actionPayload: "Production server outage reported. Escalating to on-call engineer.",
    };
  }
  if (subject.includes("newsletter") || subject.includes("this week in")) {
    return {
      category: "newsletter",
      priority: "low",
      action: "archive",
      reasoning: "Automated newsletter - no action needed",
      actionPayload: "newsletters",
    };
  }
  if (subject.includes("invoice") || subject.includes("payment")) {
    return {
      category: "billing",
      priority: "medium",
      action: "create_task",
      reasoning: "Invoice requires approval and payment action",
      actionPayload: "Review and approve invoice: " + email.subject,
    };
  }
  if (subject.includes("application") || subject.includes("applying")) {
    return {
      category: "recruitment",
      priority: "medium",
      action: "create_task",
      reasoning: "Job application needs routing to HR/hiring manager",
      actionPayload: "Review job application from " + email.from + " - " + email.subject,
    };
  }
  if (subject.includes("offsite") || subject.includes("availability")) {
    return {
      category: "scheduling",
      priority: "normal",
      action: "reply",
      reasoning: "Scheduling request needs a response",
      actionPayload:
        "Thank you for the invite! I will check my calendar and confirm by tomorrow. Best regards.",
    };
  }

  return {
    category: "general",
    priority: "normal",
    action: "archive",
    reasoning: "No specific action pattern matched",
    actionPayload: "general",
  };
}

// --- Audit Log ---------------------------------------------------------------
const auditLog = [];

function logDecision(email, classification, actionResult) {
  auditLog.push({
    timestamp: new Date().toISOString(),
    emailId: email.id,
    from: email.from,
    subject: email.subject,
    category: classification.category,
    priority: classification.priority,
    action: classification.action,
    reasoning: classification.reasoning,
    result: actionResult,
  });
}

// --- Main Agent Loop ---------------------------------------------------------
async function runEmailAgent() {
  console.log("=".repeat(60));
  console.log("EMAIL TRIAGE AGENT - AUTONOMOUS MODE");
  console.log("Processing " + INBOX.length + " emails...");
  console.log("=".repeat(60));

  for (const email of INBOX) {
    console.log("\n[" + email.id + "] From: " + email.from);
    console.log("   Subject: " + email.subject);

    const classification = classifyEmail(email);
    console.log("   Category: " + classification.category + " | Priority: " + classification.priority);
    console.log("   Reasoning: " + classification.reasoning);
    console.log("   Action: " + classification.action);

    const handler = actionHandlers[classification.action];
    const actionResult = handler
      ? handler(email, classification.actionPayload)
      : { skipped: true };

    logDecision(email, classification, actionResult);

    // Simulate processing delay between emails
    await new Promise((r) => setTimeout(r, 150));
  }

  // Print summary
  console.log("\n" + "=".repeat(60));
  console.log("TRIAGE SUMMARY");
  console.log("=".repeat(60));

  const actionCounts = {};
  const priorityCounts = {};
  auditLog.forEach((e) => {
    actionCounts[e.action] = (actionCounts[e.action] || 0) + 1;
    priorityCounts[e.priority] = (priorityCounts[e.priority] || 0) + 1;
  });

  console.log("\nActions taken:");
  Object.entries(actionCounts).forEach(([k, v]) => console.log("  " + k + ": " + v));

  console.log("\nBy priority:");
  Object.entries(priorityCounts).forEach(([k, v]) => console.log("  " + k + ": " + v));

  console.log("\n" + auditLog.length + " emails processed autonomously");
  console.log("Full audit log has " + auditLog.length + " entries (available for compliance review)");
}

runEmailAgent().catch(console.error);
