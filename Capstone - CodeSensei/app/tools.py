"""
CodeSensei — LangChain Tool Wrappers
======================================
Wrap each agent function as a LangChain Tool so the
ReAct coordinator (AgentExecutor) can call them.

Concepts used:
- LangChain Tool class (Lecture 5 & 6)
- ReAct pattern — tools are the "actions" the agent can take
- Agent orchestration via tools

═══════════════════════════════════════════════
  PART 2 (Capstone Extension) — YOUR TASKS:
    TODO 1: Create the BugDetector tool
    TODO 2: Create the StyleQuality tool
    TODO 3: Create the ConceptExplainer tool
    TODO 4: Create the ChallengeGenerator tool
    TODO 5: Create the get_all_tools() helper
═══════════════════════════════════════════════

How LangChain Tools work:
    A Tool wraps a function so the ReAct agent can call it.
    Each tool has:
    - name: A short identifier (e.g., "BugDetector")
    - func: The Python function to call
    - description: What the tool does (the agent reads this
      to decide WHEN to use the tool)

    The agent's "Thought → Action → Observation" loop:
    1. Agent THINKS: "I need to check for bugs"
    2. Agent ACTS: Calls the "BugDetector" tool
    3. Agent OBSERVES: Reads the tool's output
    4. Agent THINKS: "Now I should check code style"
    5. ... and so on
"""

from langchain.tools import Tool


# ──────────────────────────────────────────────
# TODO 1: Create the BugDetector Tool
# ──────────────────────────────────────────────
# Wrap the run_bug_detector() function as a LangChain Tool.
#
# Steps:
#   1. Import run_bug_detector from app.agents
#
#   2. Create a wrapper function that:
#      - Accepts a single string input (the agent sends
#        a string like "python|||def add(a,b): return a-b")
#      - Parses the input to extract language and code
#        (split by "|||")
#      - Calls run_bug_detector(code, language)
#      - Formats the result as a string for the agent to read
#
#   3. Create the Tool:
#      bug_detector_tool = Tool(
#          name="BugDetector",
#          func=your_wrapper_function,
#          description="Analyzes code for bugs, logic errors, "
#              "and potential runtime failures. "
#              "Input format: 'language|||code'"
#      )
#
# Why a wrapper?
#   LangChain Tools expect a function that takes a SINGLE
#   string input and returns a string output. Our agent
#   functions take multiple arguments, so we need a wrapper
#   to handle the conversion.
#
# Example:
#   Input:  "python|||def add(a,b): return a-b"
#   Output: "Bug 1: Uses subtraction... (Severity: high)\n..."

from app.agents import run_bug_detector


def _bug_detector_wrapper(tool_input: str) -> str:
    parts = tool_input.split("|||")
    if len(parts) < 2:
        return "Error: Input must be 'language|||code'"
    language, code = parts[0].strip(), parts[1].strip()
    bugs = run_bug_detector(code, language)
    if not bugs:
        return "No bugs found."
    lines = []
    for i, bug in enumerate(bugs, 1):
        lines.append(
            f"Bug {i}: {bug.bug_description} (Severity: {bug.severity.value})\n"
            f"Line: {bug.line_number or 'unknown'}\n"
            f"Suggestion: {bug.suggestion}"
        )
    return "\n\n".join(lines)

bug_detector_tool = Tool(
    name="BugDetector",
    func=_bug_detector_wrapper,
    description=(
        "Analyzes code for bugs, logic errors, and potential runtime failures. "
        "Input format: 'language|||code'"
    )
)



# ──────────────────────────────────────────────
# TODO 2: Create the StyleQuality Tool
# ──────────────────────────────────────────────
# Wrap the run_style_quality() function as a LangChain Tool.
#
# Steps:
#   1. Import run_style_quality from app.agents
#
#   2. Create a wrapper function that:
#      - Accepts input: "language|||code"
#      - Calls run_style_quality(code, language)
#      - Formats the result as a string
#
#   3. Create the Tool:
#      style_quality_tool = Tool(
#          name="StyleQuality",
#          func=your_wrapper_function,
#          description="Reviews code for naming conventions, "
#              "structure, complexity, and best practices. "
#              "Input format: 'language|||code'"
#      )

from app.agents import run_style_quality


def _style_quality_wrapper(tool_input: str) -> str:
    parts = tool_input.split("|||")
    if len(parts) < 2:
        return "Error: Input must be 'language|||code'"
    language, code = parts[0].strip(), parts[1].strip()
    issues = run_style_quality(code, language)
    if not issues:
        return "No style issues found."
    lines = []
    for i, issue in enumerate(issues, 1):
        lines.append(
            f"Issue {i}: {issue.issue} (Category: {issue.category})\n"
            f"Line: {issue.line_number or 'unknown'}\n"
            f"Suggestion: {issue.suggestion}"
        )
    return "\n\n".join(lines)

style_quality_tool = Tool(
    name="StyleQuality",
    func=_style_quality_wrapper,
    description=(
        "Reviews code for naming conventions, structure, complexity, "
        "and best practices. "
        "Input format: 'language|||code'"
    )
)


# ──────────────────────────────────────────────
# TODO 3: Create the ConceptExplainer Tool
# ──────────────────────────────────────────────
# Wrap the run_concept_explainer() function as a Tool.
#
# Steps:
#   1. Import run_concept_explainer from app.agents
#
#   2. Create a wrapper function that:
#      - Accepts input: "language|||code|||bug_report"
#      - Calls run_concept_explainer(code, language, bug_report)
#      - Formats the result as a string
#
#   3. Create the Tool:
#      concept_explainer_tool = Tool(
#          name="ConceptExplainer",
#          func=your_wrapper_function,
#          description="Explains the CS concepts behind bugs "
#              "using documentation (RAG-powered). Helps "
#              "students understand WHY issues exist. "
#              "Input format: 'language|||code|||bug_report'"
#      )
#
# Note: The description is crucial! The ReAct agent reads
# it to decide when to use this tool. Be specific about
# what the tool does and when to use it.

from app.agents import run_concept_explainer


def _concept_explainer_wrapper(tool_input: str) -> str:
    parts = tool_input.split("|||")
    if len(parts) < 3:
        return "Error: Input must be 'language|||code|||bug_report'"
    language, code, bug_report = parts[0].strip(), parts[1].strip(), parts[2].strip()
    explanations = run_concept_explainer(code, language, bug_report)
    if not explanations:
        return "No concept explanations generated."
    lines = []
    for i, exp in enumerate(explanations, 1):
        lines.append(
            f"Concept {i}: {exp.concept}\n"
            f"Explanation: {exp.explanation}\n"
            f"Related Bug: {exp.related_bug}\n"
            f"Code Example: {exp.code_example or 'none'}"
        )
    return "\n\n".join(lines)

concept_explainer_tool = Tool(
    name="ConceptExplainer",
    func=_concept_explainer_wrapper,
    description=(
        "Explains the CS concepts behind bugs using documentation (RAG-powered). "
        "Helps students understand WHY issues exist. "
        "Input format: 'language|||code|||bug_report'"
    )
)


# ──────────────────────────────────────────────
# TODO 4: Create the ChallengeGenerator Tool
# ──────────────────────────────────────────────
# Wrap the run_challenge_generator() function as a Tool.
#
# Steps:
#   1. Import run_challenge_generator from app.agents
#
#   2. Create a wrapper function that:
#      - Accepts input: "language|||bug_report|||style_report"
#      - Calls run_challenge_generator(language, bug_report, style_report)
#      - Formats the result as a string
#
#   3. Create the Tool:
#      challenge_generator_tool = Tool(
#          name="ChallengeGenerator",
#          func=your_wrapper_function,
#          description="Creates follow-up coding challenges "
#              "based on the student's weak spots. Should be "
#              "called AFTER bug detection and style review. "
#              "Input format: 'language|||bug_report|||style_report'"
#      )

from app.agents import run_challenge_generator


def _challenge_generator_wrapper(tool_input: str) -> str:
    parts = tool_input.split("|||")
    if len(parts) < 3:
        return "Error: Input must be 'language|||bug_report|||style_report'"
    language, bug_report, style_report = parts[0].strip(), parts[1].strip(), parts[2].strip()
    challenges = run_challenge_generator(language, bug_report, style_report)
    if not challenges:
        return "No challenges generated."
    lines = []
    for i, ch in enumerate(challenges, 1):
        lines.append(
            f"Challenge {i}: {ch.title} (Difficulty: {ch.difficulty})\n"
            f"Description: {ch.description}\n"
            f"Starter Code:\n{ch.starter_code}\n"
            f"Hint: {ch.hint or 'none'}"
        )
    return "\n\n".join(lines)

challenge_generator_tool = Tool(
    name="ChallengeGenerator",
    func=_challenge_generator_wrapper,
    description=(
        "Creates follow-up coding challenges based on the student's weak spots. "
        "Should be called AFTER bug detection and style review. "
        "Input format: 'language|||bug_report|||style_report'"
    )
)


# ──────────────────────────────────────────────
# TODO 5: Create the get_all_tools() helper
# ──────────────────────────────────────────────
# This function returns a list of all tools for the
# ReAct agent to use.
#
# def get_all_tools():
#     """Return all available tools for the ReAct agent."""
#     return [
#         bug_detector_tool,
#         style_quality_tool,
#         concept_explainer_tool,
#         challenge_generator_tool,
#     ]

def get_all_tools():
    """Return all available tools for the ReAct agent."""
    return [
        bug_detector_tool,
        style_quality_tool,
        concept_explainer_tool,
        challenge_generator_tool,
    ]