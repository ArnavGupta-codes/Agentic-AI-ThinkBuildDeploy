# 🥋CodeSensei — AI-Powered Code Review & Learning Platform

> **Capstone Project** — Build a multi-agent AI system that reviews code, finds bugs, and helps students learn.

---

## What You're Building

CodeSensei is a **multi-agent AI system** that takes a student's code as input and returns:

### Part 1 (Eval 2) — The Foundation
1. **Bug Detection** — Identifies logic errors, syntax issues, and edge cases
2. **Fix Suggestions** — Explains how to fix each bug
3. **Quality Score** — Rates the code from 0-100
4. **Learning Summary** — Educational feedback to help the student improve

### Part 2 (Capstone Extension) — Full Multi-Agent System
5. **Style & Quality Review** — Naming conventions, structure, complexity analysis
6. **Concept Explanations** — RAG-powered explanations of *why* issues exist
7. **Coding Challenges** — Follow-up exercises based on weak spots
8. **🎤 Voice-to-Text Input** — Speak your code aloud and get it reviewed!
9. **ReAct Agent Orchestration** — Transparent "Thought → Action → Observation" loops
10. **Docker Deployment** — Containerized production setup

You'll build this using **LangChain** for agent orchestration, **FastAPI** for the REST API, and **Gemini** for the LLM.

### System Overview

**Part 1 — Basic Pipeline:**
```
Student Code -> POST /review-code -> Coordinator Agent
                                        |
                                   Bug Detector Agent -> Gemini LLM
                                        |
                                   Parse Bugs -> Score + Summary
                                        |
                                   JSON Response <- ReviewResponse
```

**Part 2 — ReAct Multi-Agent Pipeline:**
```
Student Code/Audio -> POST /review-code-advanced
                      POST /review-voice
                              |
                    ┌─── ReAct Coordinator (AgentExecutor) ───┐
                    │   Thought → Action → Observation loops   │
                    ├──→ 🔧 BugDetector Tool                   │
                    ├──→ 🔧 StyleQuality Tool                  │
                    ├──→ 🔧 ConceptExplainer Tool (+ RAG)      │
                    ├──→ 🔧 ChallengeGenerator Tool            │
                    └──→ FullReviewResponse (JSON)             │
                    └──────────────────────────────────────────┘
```

> See [`docs/architecture.md`](docs/architecture.md) for the full architecture diagrams.

---

## Concepts Used (Lecture Mapping)

| Lecture | Topic | Where It's Used |
|---------|-------|-----------------| 
| L2 | Environment Mastery | Virtual env, `.env`, dependencies |
| L3 | RAG Revolution | LangChain, PromptTemplate, LLM chains, ChromaDB |
| L4 | State & Memory | LangChain patterns, chain composition |
| L5 | Agentic AI Systems | Multi-agent design, autonomous agents |
| L6 | Agent Control Flow | Agent orchestration, ReAct loops, AgentExecutor |
| L7 | Docker | Dockerfile, docker-compose, containerization |
| L8 | Production Backend | FastAPI, REST endpoints, Pydantic validation |

---

## Project Structure

```
Capstone - CodeSensei/
├── README.md               <- You are here
├── requirements.txt        <- Python dependencies
├── .env.example            <- Template for API keys
├── .gitignore
├── Dockerfile              <- [Part 2] Container config
├── docker-compose.yml      <- [Part 2] Multi-service setup
│
├── app/
│   ├── __init__.py
│   ├── config.py           <- PROVIDED — LLM connection & env setup
│   ├── schemas.py          <- TODO — Define Pydantic data models
│   ├── prompts.py          <- TODO — Write LangChain PromptTemplates
│   ├── agents.py           <- TODO — Implement agent logic & parsing
│   ├── main.py             <- TODO — Build the FastAPI endpoints
│   ├── tools.py            <- [Part 2] TODO — LangChain Tool wrappers
│   └── voice.py            <- [Part 2] TODO — Voice-to-Text module
│
├── tests/
│   ├── __init__.py
│   └── test_review.py      <- Tests to verify your implementations
│
└── docs/
    └── architecture.md     <- System architecture diagrams
```

---

## Setup Instructions

### 1. Create a Virtual Environment

```bash
cd "Capstone - CodeSensei"
python3 -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate        # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Your API Key

```bash
cp .env.example .env
# Edit .env and add your Gemini API key
# Get one at: https://aistudio.google.com/apikey
```

### 4. Verify Setup

```bash
python -c "from app.config import llm; print('Setup complete!')"
```

You should see:
```
Gemini LLM initialized successfully!
Setup complete!
```

---

## Your TODO Checklist

### ═══ PART 1: Eval 2 ═══

Complete these in order — each step builds on the previous one.

#### Step 1: Define the Data Models (`app/schemas.py`)

| TODO | What to Do | Hint |
|------|-----------|------|
| TODO 1 | Define `CodeReviewRequest` fields | `code: str`, `language: Language`, `context: Optional[str]` |
| TODO 2 | Define `BugReport` fields | `bug_description`, `severity`, `suggestion`, `line_number` |
| TODO 3 | Define `ReviewResponse` fields | `bugs: List[BugReport]`, `summary`, `score` (0-100) |

**Verify:** `pytest tests/test_review.py::test_code_review_request_valid -v`

#### Step 2: Write the Prompt Templates (`app/prompts.py`)

| TODO | What to Do | Key Point |
|------|-----------|-----------| 
| TODO 1 | Write `BUG_DETECTOR_PROMPT` | Must output in exact format: `BUG:`, `SEVERITY:`, `LINE:`, `SUGGESTION:`, `---` |
| TODO 2 | Write `COORDINATOR_PROMPT` | Must output: `SUMMARY:` and `SCORE:` |

**Key Concept:** The prompts define the *behavior* of each agent. The output format must be exact because the parser depends on it!

#### Step 3: Implement the Agent Logic (`app/agents.py`)

| TODO | What to Do | Key Concept |
|------|-----------|------------|
| TODO 1 | Implement `parse_bug_report()` | String parsing into Pydantic objects |
| TODO 2 | Implement `run_bug_detector()` | Use `BUG_DETECTOR_PROMPT \| llm` chain |
| TODO 3 | Implement `run_coordinator()` | Orchestrate: bug detector -> coordinator LLM -> response |

**Verify:** `pytest tests/test_review.py::test_parse_bug_report_single_bug -v`

#### Step 4: Build the API Endpoint (`app/main.py`)

| TODO | What to Do | Key Concept |
|------|-----------|------------|
| TODO 1 | Implement `POST /review-code` | Call `run_coordinator()`, handle errors with `HTTPException` |

**Verify:** Start the server and test with curl (see below)

---

### ═══ PART 2: Capstone Extension ═══

Complete these AFTER finishing all Part 1 TODOs. Part 2 extends CodeSensei with additional agents, Voice-to-Text input, and Docker deployment.

#### Step 5: Extended Data Models (`app/schemas.py`)

| TODO | What to Do | Hint |
|------|-----------|------|
| TODO 4 | Define `StyleIssue` | `issue`, `category`, `suggestion`, `line_number` |
| TODO 5 | Define `ConceptExplanation` | `concept`, `explanation`, `related_bug`, `resource_link`, `code_example` |
| TODO 6 | Define `CodingChallenge` | `title`, `description`, `difficulty`, `starter_code`, `hint` |
| TODO 7 | Define `FullReviewResponse` | All agent outputs + `reasoning_trace` |
| TODO 8 | Define `VoiceReviewRequest` | `language`, `context`, `use_advanced` |

**Verify:** Uncomment and run Part 2 tests in `test_review.py`

#### Step 6: Extended Prompt Templates (`app/prompts.py`)

| TODO | What to Do | Key Point |
|------|-----------|-----------| 
| TODO 3 | Write `STYLE_QUALITY_PROMPT` | Output: `ISSUE:`, `CATEGORY:`, `LINE:`, `SUGGESTION:`, `---` |
| TODO 4 | Write `CONCEPT_EXPLAINER_PROMPT` | Uses `{rag_context}` from ChromaDB |
| TODO 5 | Write `CHALLENGE_GENERATOR_PROMPT` | Output: `TITLE:`, `DESCRIPTION:`, `DIFFICULTY:`, `STARTER_CODE:`, `HINT:`, `---` |
| TODO 6 | Write `TRANSCRIPT_PARSER_PROMPT` | Converts spoken code to formatted code |

#### Step 7: Extended Agent Logic (`app/agents.py`)

| TODO | What to Do | Key Concept |
|------|-----------|------------|
| TODO 4 | Implement `run_style_quality()` | Same pattern as bug detector |
| TODO 5 | Implement `run_concept_explainer()` | RAG retrieval from ChromaDB + LLM |
| TODO 6 | Implement `run_challenge_generator()` | Creates exercises from weak spots |
| TODO 7 | Implement `run_react_coordinator()` | LangChain `AgentExecutor` + `create_react_agent` |

**Key Concept:** The ReAct coordinator uses "Thought → Action → Observation" loops. It dynamically calls tools based on what it learns!

#### Step 8: LangChain Tool Wrappers (`app/tools.py`)

| TODO | What to Do | Key Concept |
|------|-----------|------------|
| TODO 1 | Create `BugDetector` tool | Wrap agent function as LangChain `Tool` |
| TODO 2 | Create `StyleQuality` tool | Input format: `"language\|\|\|code"` |
| TODO 3 | Create `ConceptExplainer` tool | Input format: `"language\|\|\|code\|\|\|bug_report"` |
| TODO 4 | Create `ChallengeGenerator` tool | Input format: `"language\|\|\|bug_report\|\|\|style_report"` |
| TODO 5 | Implement `get_all_tools()` | Returns list of all tools |

#### Step 9: Voice-to-Text Module (`app/voice.py`)

| TODO | What to Do | Key Concept |
|------|-----------|------------|
| TODO 1 | Implement `transcribe_audio()` | Gemini multimodal API (audio → text) |
| TODO 2 | Implement `extract_code_from_transcript()` | Spoken language → formatted code |

**Key Concept:** `transcribe_audio()` uses Gemini's native audio support. The student speaks their code, Gemini transcribes it, then the LLM converts the transcript into properly formatted code.

#### Step 10: Extended API Endpoints (`app/main.py`)

| TODO | What to Do | Key Concept |
|------|-----------|------------|
| TODO 2 | Implement `POST /review-code-advanced` | Uses ReAct coordinator with all agents |
| TODO 3 | Implement `POST /review-voice` | Audio upload → transcribe → review |

---

## Running the Application

### Start the Server

```bash
python -m uvicorn app.main:app --reload --port 8000
```

### Test with curl

```bash
# Health check
curl http://localhost:8000/health

# Part 1: Basic review
curl -X POST http://localhost:8000/review-code \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b):\n    return a - b",
    "language": "python",
    "context": "Simple addition function"
  }'

# Part 2: Advanced review (all agents)
curl -X POST http://localhost:8000/review-code-advanced \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b):\n    return a - b",
    "language": "python",
    "context": "Simple addition function"
  }'

# Part 2: Voice review
curl -X POST http://localhost:8000/review-voice \
  -F "audio=@my_code.wav" \
  -F "language=python" \
  -F "context=Sorting function" \
  -F "use_advanced=false"
```

### Test with the Swagger UI

Open your browser to: **http://localhost:8000/docs**

FastAPI auto-generates an interactive API documentation page where you can test your endpoint directly!

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_review.py::test_code_review_request_valid -v
```

### Docker Deployment (Part 2)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build just the app
docker build -t codesensei .
docker run -p 8000:8000 --env-file .env codesensei
```

---

## Tips

1. **Work in order** — Part 1 first, then Part 2. Each builds on the last.
2. **Read the comments** — Every TODO has step-by-step instructions and examples.
3. **Test frequently** — Run the relevant test after completing each TODO.
4. **Prompt engineering matters** — The quality of your prompts directly affects the quality of reviews. Experiment!
5. **Use the pipe operator** — `chain = prompt | llm` is LangChain's modern syntax for chaining.
6. **Handle edge cases** — What if the LLM returns unexpected output? Use try/except.
7. **Check the architecture** — `docs/architecture.md` has Mermaid diagrams showing the full data flow.

---

## Example Input/Output

### Part 1: Basic Review

**Input:**
```python
def find_max(numbers):
    max_num = 0
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num
```

**Expected Response:**
```json
{
  "bugs": [
    {
      "bug_description": "Initial value of 0 fails for lists with only negative numbers",
      "severity": "high",
      "suggestion": "Initialize max_num to float('-inf') or numbers[0]",
      "line_number": 2
    },
    {
      "bug_description": "No handling for empty list input",
      "severity": "medium",
      "suggestion": "Add a check: if not numbers: return None",
      "line_number": 1
    }
  ],
  "summary": "Found 2 bugs. The main issue is the initialization of max_num to 0...",
  "score": 55,
  "language": "python"
}
```

### Part 2: Advanced Review (excerpt)

**Same input, but via `/review-code-advanced`:**
```json
{
  "bugs": [...],
  "style_issues": [
    {
      "issue": "No type hints on function parameters",
      "category": "best_practice",
      "suggestion": "Add type hint: def find_max(numbers: list[int]) -> int:",
      "line_number": 1
    }
  ],
  "explanations": [
    {
      "concept": "Sentinel values and initialization",
      "explanation": "When finding extremes in a collection, initializing with 0 assumes...",
      "related_bug": "Initial value of 0 fails for negative numbers",
      "code_example": "max_num = float('-inf')  # Works for any numeric input"
    }
  ],
  "challenges": [
    {
      "title": "Handle All Edge Cases",
      "description": "Modify find_max to handle empty lists, single elements, and all-negative lists",
      "difficulty": "medium",
      "starter_code": "def find_max(numbers):\n    # Handle edge cases\n    pass",
      "hint": "Consider what should happen for find_max([]) and find_max([-5, -3, -8])"
    }
  ],
  "summary": "Found 2 bugs and 1 style issue...",
  "score": 55,
  "language": "python",
  "reasoning_trace": "Thought: I should first check for bugs...\nAction: BugDetector\n..."
}
```

---

## Resources

- [LangChain Docs](https://python.langchain.com/docs/)
- [LangChain Tools Guide](https://python.langchain.com/docs/how_to/custom_tools/)
- [LangChain ReAct Agent](https://python.langchain.com/docs/how_to/agent_executor/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [FastAPI File Uploads](https://fastapi.tiangolo.com/tutorial/request-files/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Google Gemini API](https://ai.google.dev/)
- [Gemini Multimodal (Audio)](https://ai.google.dev/gemini-api/docs/audio)

---

*Built for the "Build & Deploy AI Agents" course — Capstone Project*
