/**
 * Agent Worker + Job Queue
 *
 * Production pattern: tasks go into a priority queue, workers pick them up.
 * Simulates a real deployment where multiple agent workers process jobs
 * concurrently with retry logic and event-based status tracking.
 *
 * Run: node worker.js
 */

const { EventEmitter } = require("events");

// --- Simple In-Memory Priority Job Queue ------------------------------------
class JobQueue extends EventEmitter {
  constructor() {
    super();
    this.pending = [];
    this.running = new Map();
    this.completed = [];
    this.failed = [];
  }

  enqueue(job) {
    const entry = {
      id: "job_" + Date.now() + "_" + Math.random().toString(36).slice(2, 8),
      task: job.task,
      priority: job.priority || 0,
      retries: 0,
      maxRetries: job.maxRetries || 3,
      createdAt: new Date().toISOString(),
      status: "pending",
    };
    this.pending.push(entry);
    // Higher priority value = processed first
    this.pending.sort((a, b) => b.priority - a.priority);
    console.log("Enqueued job " + entry.id + ': "' + entry.task.slice(0, 50) + '..."');
    this.emit("job:enqueued", entry);
    return entry.id;
  }

  dequeue() {
    return this.pending.shift() || null;
  }

  complete(jobId, result) {
    const job = this.running.get(jobId);
    if (!job) return;
    job.status = "completed";
    job.result = result;
    job.completedAt = new Date().toISOString();
    this.running.delete(jobId);
    this.completed.push(job);
    this.emit("job:completed", job);
  }

  fail(jobId, error) {
    const job = this.running.get(jobId);
    if (!job) return;
    job.retries++;
    if (job.retries < job.maxRetries) {
      // Re-queue for retry
      job.status = "pending";
      this.running.delete(jobId);
      this.pending.unshift(job);
      console.log("Job " + jobId + " re-queued (attempt " + job.retries + "/" + job.maxRetries + ")");
      this.emit("job:retry", job);
    } else {
      // Permanently failed
      job.status = "failed";
      job.error = error;
      job.failedAt = new Date().toISOString();
      this.running.delete(jobId);
      this.failed.push(job);
      this.emit("job:failed", job);
    }
  }

  stats() {
    return {
      pending: this.pending.length,
      running: this.running.size,
      completed: this.completed.length,
      failed: this.failed.length,
    };
  }
}

// --- Agent Worker ------------------------------------------------------------
class AgentWorker {
  constructor(id, queue) {
    this.id = id;
    this.queue = queue;
    this.busy = false;
  }

  // Simulates an AI agent processing a task.
  // In real deployment, this calls the Claude API with tools.
  async processTask(task) {
    const delay = (ms) => new Promise((r) => setTimeout(r, ms));

    const steps = [];
    steps.push("[Worker " + this.id + '] Received task: "' + task + '"');

    await delay(200);
    steps.push("[Worker " + this.id + "] Analyzing task requirements...");

    await delay(300);
    const toolNeeded = task.toLowerCase().includes("calculate")
      ? "calculator"
      : task.toLowerCase().includes("search")
      ? "search"
      : task.toLowerCase().includes("report")
      ? "write_file"
      : "reasoning";
    steps.push("[Worker " + this.id + "] Using tool: " + toolNeeded);

    await delay(400);
    steps.push("[Worker " + this.id + "] Task completed.");

    return { steps, output: 'Processed: "' + task + '" using ' + toolNeeded };
  }

  async run() {
    console.log("Worker " + this.id + " started");

    while (true) {
      const job = this.queue.dequeue();

      if (!job) {
        // Exit when queue is empty and nothing is running
        if (!this.queue.pending.length && !this.queue.running.size) break;
        await new Promise((r) => setTimeout(r, 100));
        continue;
      }

      this.busy = true;
      job.status = "running";
      job.startedAt = new Date().toISOString();
      job.workerId = this.id;
      this.queue.running.set(job.id, job);

      console.log("\nWorker " + this.id + " processing job " + job.id);

      try {
        const result = await this.processTask(job.task);
        this.queue.complete(job.id, result);
        console.log("Worker " + this.id + " completed job " + job.id);
        result.steps.forEach((s) => console.log("   " + s));
      } catch (err) {
        this.queue.fail(job.id, err.message);
        console.log("Worker " + this.id + " failed job " + job.id + ": " + err.message);
      }

      this.busy = false;
    }

    console.log("Worker " + this.id + " done");
  }
}

// --- Main --------------------------------------------------------------------
async function main() {
  console.log("=== Agent Worker Queue Demo ===\n");

  const queue = new JobQueue();

  queue.on("job:completed", () => {
    console.log("\nQueue stats: " + JSON.stringify(queue.stats()));
  });
  queue.on("job:failed", (job) => {
    console.error("\nJob permanently failed: " + job.id + " - " + job.error);
  });

  // Enqueue jobs with different priorities (higher number = higher priority)
  queue.enqueue({ task: "Summarize the quarterly financial report for Q1 2026", priority: 2 });
  queue.enqueue({ task: "Search for all pending customer support tickets", priority: 1 });
  queue.enqueue({ task: "Calculate ROI for the new product launch campaign", priority: 3 });
  queue.enqueue({ task: "Write a report on agent deployment best practices", priority: 1 });
  queue.enqueue({ task: "Analyze user feedback and generate action items", priority: 2 });

  console.log("\nInitial queue stats: " + JSON.stringify(queue.stats()) + "\n");

  // Start 2 parallel workers
  const workers = [new AgentWorker("A", queue), new AgentWorker("B", queue)];
  await Promise.all(workers.map((w) => w.run()));

  console.log("\n=== Final Queue Stats ===");
  console.log(JSON.stringify(queue.stats(), null, 2));
  console.log("\nAll jobs processed.");
}

main().catch(console.error);
