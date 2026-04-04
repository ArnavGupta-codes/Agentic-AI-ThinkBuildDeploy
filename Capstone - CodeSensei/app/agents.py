"""
CodeSensei — Agent Logic
=========================
This file contains the core agent functions that use
LangChain to call the LLM with our prompt templates.

Concepts used:
- LangChain LLMChain / RunnableSequence (Lecture 3 & 4)
- Output parsing & string manipulation
- Multi-agent orchestration (Lecture 5 & 6)

YOUR TASKS:
  TODO 1: Implement the parse_bug_report() helper
  TODO 2: Implement the run_bug_detector() agent
  TODO 3: Implement the run_coordinator() agent
"""

from typing import List
from app.config import llm
from app.prompts import BUG_DETECTOR_PROMPT, COORDINATOR_PROMPT
from app.schemas import BugReport, ReviewResponse, Severity


# ──────────────────────────────────────────────
# Helper: Parse Bug Detector Output (PROVIDED)
# ──────────────────────────────────────────────
# This helper parses the structured text output from
# the Bug Detector LLM into a list of BugReport objects.
#
# Expected input format (from the Bug Detector prompt):
#   BUG: <description>
#   SEVERITY: <critical|high|medium|low>
#   LINE: <number or "unknown">
#   SUGGESTION: <fix>
#   ---
#
# If the output contains "NO_BUGS_FOUND", returns [].

def parse_bug_report(raw_output: str) -> List[BugReport]:
    """
    Parse the raw text output from the Bug Detector
    into a list of BugReport Pydantic models.

    Args:
        raw_output: Raw string output from the LLM

    Returns:
        List of BugReport objects
    """
    # ──────────────────────────────────────────
    # TODO 1: Implement the parsing logic
    # ──────────────────────────────────────────
    # Steps:
    #   1. Check if raw_output contains "NO_BUGS_FOUND"
    #      → If yes, return an empty list []
    #
    #   2. Split the raw_output by "---" to get individual bug blocks
    #
    #   3. For each block, extract the fields:
    #      - Find "BUG:" line → bug_description
    #      - Find "SEVERITY:" line → map to Severity enum
    #      - Find "LINE:" line → convert to int (or None if "unknown")
    #      - Find "SUGGESTION:" line → suggestion text
    #
    #   4. Create a BugReport object for each block and add to list
    #
    #   5. Return the list of BugReport objects
    #
    # Hints:
    #   - Use str.split("---") to split into blocks
    #   - Use str.strip() to clean whitespace
    #   - Use a for loop over lines in each block
    #   - Handle cases where a field might be missing (use defaults)
    #   - Wrap in try/except to handle malformed output gracefully
    #
    # Example:
    #   raw = "BUG: Off by one\nSEVERITY: high\nLINE: 5\nSUGGESTION: Use < instead of <=\n---"
    #   result = [BugReport(bug_description="Off by one", severity=Severity.HIGH, ...)]

    #pass  # ← Replace this with your implementation
    if "NO_BUGS_FOUND" in raw_output:
        return []
    
    bugs=[]
    blocks = raw_output.split("---")
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        bug_description = ""             #initialise variables
        severity = Severity.LOW
        line_number = None
        suggestion = ""

        lines = block.split("\n")

        for line in lines:
            line = line.strip()

            if line.startswith("BUG:"):
                bug_description = line.replace("BUG:", "").strip()

            elif line.startswith("SEVERITY:"):
                sev = line.replace("SEVERITY:", "").strip().lower()
                if sev in Severity._value2member_map_:
                    severity = Severity(sev)

            elif line.startswith("LINE:"):
                line_val = line.replace("LINE:", "").strip()
                if line_val.lower() != "unknown":
                    try:
                        line_number = int(line_val)
                    except:
                        line_number = None

            elif line.startswith("SUGGESTION:"):
                suggestion = line.replace("SUGGESTION:", "").strip()

        try:
            bug = BugReport(
                bug_description=bug_description,
                severity=severity,
                suggestion=suggestion,
                line_number=line_number
            )
            bugs.append(bug)
        except:
            continue

    return bugs



# ──────────────────────────────────────────────
# Agent 1: Bug Detector ("The Grader")
# ──────────────────────────────────────────────

def run_bug_detector(code: str, language: str) -> List[BugReport]:
    """
    Analyze code for bugs using the Bug Detector prompt + LLM.

    This function creates a LangChain chain (prompt | llm),
    invokes it with the code, and parses the output into
    BugReport objects.

    Args:
        code: Source code string to analyze
        language: Programming language (e.g., "python")

    Returns:
        List of BugReport objects found in the code
    """
    # ──────────────────────────────────────────
    # TODO 2: Implement the Bug Detector agent
    # ──────────────────────────────────────────
    # Steps:
    #   1. Create a LangChain chain using the pipe operator:
    #      chain = BUG_DETECTOR_PROMPT | llm
    #
    #   2. Invoke the chain with the input variables:
    #      result = chain.invoke({"code": code, "language": language})
    #
    #   3. Extract the text content from the result:
    #      raw_output = result.content
    #      (LangChain returns an AIMessage object, .content gives the text)
    #
    #   4. Parse the raw output into BugReport objects:
    #      bugs = parse_bug_report(raw_output)
    #
    #   5. Return the list of bugs
    #
    # Concepts:
    #   - The pipe operator (|) creates a RunnableSequence
    #     This is LangChain's modern way of chaining components
    #     (replaces the older LLMChain approach)
    #   - .invoke() runs the chain with the given inputs
    #   - The LLM returns an AIMessage; use .content to get text

    #pass  # ← Replace this with your implementation
    chain = BUG_DETECTOR_PROMPT | llm

    result = chain.invoke({
        "code": code,
        "language": language
    })

    raw_output = result.content

    bugs = parse_bug_report(raw_output)

    return bugs


# ──────────────────────────────────────────────
# Agent 2: Coordinator ("The Orchestrator")
# ──────────────────────────────────────────────

def run_coordinator(code: str, language: str, context: str = "") -> ReviewResponse:
    """
    Orchestrate the full review process:
    1. Call Bug Detector to find bugs
    2. Use Coordinator prompt to create a summary
    3. Return a complete ReviewResponse

    This is the main entry point that main.py calls.

    Args:
        code: Source code to review
        language: Programming language
        context: Optional additional context

    Returns:
        ReviewResponse with bugs, summary, and score
    """
    # ──────────────────────────────────────────
    # TODO 3: Implement the Coordinator agent
    # ──────────────────────────────────────────
    # Steps:
    #   1. Call run_bug_detector() to get the list of bugs:
    #      bugs = run_bug_detector(code, language)
    #
    #   2. Format the bugs into a string for the Coordinator prompt:
    #      - If no bugs: bug_report_text = "No bugs found."
    #      - If bugs exist: create a readable string from the BugReport objects
    #        e.g., "Bug 1: <description> (Severity: <sev>)\n..."
    #
    #   3. Create the Coordinator chain:
    #      chain = COORDINATOR_PROMPT | llm
    #
    #   4. Invoke the chain with all input variables:
    #      result = chain.invoke({
    #          "code": code,
    #          "language": language,
    #          "bug_report": bug_report_text,
    #          "context": context or "No additional context"
    #      })
    #
    #   5. Parse the Coordinator output to extract SUMMARY and SCORE:
    #      - Find the line starting with "SUMMARY:" → extract the text
    #      - Find the line starting with "SCORE:" → extract the number
    #      - Handle edge cases (missing fields, invalid score, etc.)
    #
    #   6. Create and return the ReviewResponse:
    #      return ReviewResponse(
    #          bugs=bugs,
    #          summary=<extracted summary>,
    #          score=<extracted score>,
    #          language=language
    #      )
    #
    # Hints:
    #   - Use a try/except block for robustness
    #   - If score parsing fails, default to 50
    #   - If summary parsing fails, use the raw LLM output as summary

    #pass  # ← Replace this with your implementation
    
    # Step 1: Get bugs
    bugs = run_bug_detector(code, language)

    # Step 2: Format bug report text
    if not bugs:
        bug_report_text = "No bugs found."
    else:
        bug_report_text = ""
        for i, bug in enumerate(bugs, 1):
            bug_report_text += f"Bug {i}: {bug.bug_description} (Severity: {bug.severity.value})\n"

    # Step 3: Run coordinator LLM
    chain = COORDINATOR_PROMPT | llm

    result = chain.invoke({
        "code": code,
        "language": language,
        "bug_report": bug_report_text,
        "context": context or "No additional context"
    })

    output = result.content

    # Step 4: Parse summary and score
    summary = output
    score = 50

    try:
        lines = output.split("\n")
        for line in lines:
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()

            elif line.startswith("SCORE:"):
                score_str = line.replace("SCORE:", "").strip()
                score = int(score_str)
    except:
        pass

    # Step 5: Return structured response
    return ReviewResponse(
        bugs=bugs,
        summary=summary,
        score=score,
        language=language
    )