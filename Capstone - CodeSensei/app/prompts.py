"""
CodeSensei — Prompt Templates
==============================
Define the LangChain PromptTemplates used by each agent.

Concepts used:
- LangChain PromptTemplate (Lecture 3 & 4)
- Prompt engineering best practices
- Input variables and template formatting

YOUR TASKS:
  TODO 1: Create the Bug Detector prompt template
  TODO 2: Create the Coordinator prompt template
"""

from langchain.prompts import PromptTemplate


# ──────────────────────────────────────────────
# TODO 1: Bug Detector Prompt Template
# ──────────────────────────────────────────────
# The Bug Detector agent analyzes code to find bugs.
# Your prompt should instruct the LLM to:
#
#   1. Analyze the provided code for bugs
#   2. For EACH bug found, output in this EXACT format:
#      BUG: <description of the bug>
#      SEVERITY: <critical|high|medium|low>
#      LINE: <line number or "unknown">
#      SUGGESTION: <how to fix it>
#      ---
#   3. If no bugs found, output: NO_BUGS_FOUND
#
# Input variables (these will be filled in at runtime):
#   - {code}      → The source code to analyze
#   - {language}  → The programming language
#
# Tips for a good prompt:
#   - Be specific about the output format (the parser depends on it!)
#   - Ask it to check for: logic errors, syntax issues, edge cases,
#     off-by-one errors, null/None handling, type mismatches
#   - Tell it to be thorough but not nitpicky
#
# Example:
#   BUG_DETECTOR_PROMPT = PromptTemplate(
#       input_variables=["code", "language"],
#       template="""You are a ... 
#       
#       Code ({language}):
#       ```
#       {code}
#       ```
#       
#       ... your instructions ...
#       """
#   )

BUG_DETECTOR_PROMPT = PromptTemplate(
    input_variables=["code", "language"],
    template="""You are an expert code reviewer.
Analyze the following {language} code and identify bugs. Check for:
- Logic errors
- Syntax issues
- Edge cases
- Off-by-one errors
- Null/None handling
- Type mismatches

IMPORTANT RULES:
- Report each bug as a SEPARATE block. Do not merge multiple bugs into one.
- Every field (BUG, SEVERITY, LINE, SUGGESTION) must be on exactly ONE line. No line breaks within a field.
- Keep descriptions concise and on a single line.

For EACH bug found, output in EXACTLY this format:
BUG: <one-line description of this specific bug>
SEVERITY: <critical|high|medium|low>
LINE: <line number or "unknown">
SUGGESTION: <one-line fix suggestion>
---

If no bugs are found, output exactly:
NO_BUGS_FOUND

Code:
{code}
"""
)



# ──────────────────────────────────────────────
# TODO 2: Coordinator Prompt Template
# ──────────────────────────────────────────────
# The Coordinator agent takes the raw bug detector output
# and creates a final, student-friendly review summary.
#
# Your prompt should instruct the LLM to:
#   1. Summarize the bugs found in a helpful, educational tone
#   2. Give an overall code quality score from 0-100
#   3. Output in this EXACT format:
#      SUMMARY: <a 2-3 sentence summary of the review>
#      SCORE: <number from 0-100>
#
# Input variables:
#   - {code}              → The original source code
#   - {language}          → The programming language
#   - {bug_report}        → Output from the Bug Detector agent
#   - {context}           → Additional context from the student (may be empty)
#
# Tips:
#   - Be encouraging but honest
#   - Score guide: 90-100 = excellent, 70-89 = good, 50-69 = needs work, <50 = significant issues
#   - The summary should help the student LEARN, not just list errors
#
# Example:
#   COORDINATOR_PROMPT = PromptTemplate(
#       input_variables=["code", "language", "bug_report", "context"],
#       template="""You are a ...
#       
#       ... your instructions ...
#       """
#   )

COORDINATOR_PROMPT = PromptTemplate(
    input_variables=["code", "language", "bug_report", "context"],
    template="""You are a helpful coding mentor.
A student submitted the following {language} code:
{code}
Context from student:
{context}
Here is the bug analysis:
{bug_report}
Your job is to:
1. Write a clear and helpful summary of the issues
2. Help the student understand how to improve
3. Assign a score from 0 to 100
Tips:
- Be encouraging but honest
- Score guide: 90-100 = excellent, 70-89 = good, 50-69 = needs work, <50 = significant issues
- The summary should help the student LEARN, not just list errors

Output in EXACTLY this format:
SUMMARY: <2-3 sentence helpful explanation>
SCORE: <number between 0 and 100>
"""
)