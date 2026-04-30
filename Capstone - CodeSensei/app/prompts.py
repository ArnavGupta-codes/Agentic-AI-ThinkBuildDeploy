"""
CodeSensei — Prompt Templates
==============================
Define the LangChain PromptTemplates used by each agent.

Concepts used:
- LangChain PromptTemplate (Lecture 3 & 4)
- Prompt engineering best practices
- Input variables and template formatting

═══════════════════════════════════════════════
  PART 1 (Eval 2) — YOUR TASKS:
    TODO 1: Create the Bug Detector prompt template
    TODO 2: Create the Coordinator prompt template

  PART 2 (Capstone Extension) — YOUR TASKS:
    TODO 3: Create the Style & Quality prompt template
    TODO 4: Create the Concept Explainer prompt template
    TODO 5: Create the Challenge Generator prompt template
    TODO 6: Create the Transcript Parser prompt template
═══════════════════════════════════════════════
"""

from langchain.prompts import PromptTemplate


# ╔═══════════════════════════════════════════════╗
# ║            PART 1 — Eval 2 TODOs              ║
# ╚═══════════════════════════════════════════════╝


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
# The Coordinator agent takes the bug report and creates
# a helpful, educational summary + score for the student.
#
# Your prompt should instruct the LLM to:
#   1. Read the student's code and the bug report
#   2. Write a friendly, encouraging 2-3 sentence summary
#   3. Give an overall code quality score (0-100):
#      - 90-100: Excellent, minimal or no issues
#      - 70-89: Good, minor issues only
#      - 50-69: Needs work, some notable bugs
#      - Below 50: Significant issues that need attention
#   4. Output in this EXACT format:
#      SUMMARY: <your summary>
#      SCORE: <number>
#
# Input variables:
#   - {code}       → The source code
#   - {language}   → The programming language
#   - {bug_report} → Formatted bug report from Bug Detector
#   - {context}    → Additional context from the student
#
# Example:
#   COORDINATOR_PROMPT = PromptTemplate(
#       input_variables=["code", "language", "bug_report", "context"],
#       template="""You are a friendly mentor...
#       ...
#       SUMMARY: <summary>
#       SCORE: <number>"""   
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

# ╔═══════════════════════════════════════════════╗
# ║       PART 2 — Capstone Extension TODOs        ║
# ╚═══════════════════════════════════════════════╝
# Complete these AFTER finishing Part 1.
# These power the additional agents in CodeSensei.


# ──────────────────────────────────────────────
# TODO 3: Style & Quality Prompt Template
# ──────────────────────────────────────────────
# The Style & Quality agent reviews code for naming,
# structure, complexity, and best practices.
#
# Your prompt should instruct the LLM to:
#   1. Analyze the code for style and quality issues
#   2. Check for: naming conventions, function length,
#      code duplication, proper documentation, complexity
#   3. For EACH issue found, output in this EXACT format:
#      ISSUE: <description of the style issue>
#      CATEGORY: <naming|structure|complexity|best_practice>
#      LINE: <line number or "unknown">
#      SUGGESTION: <how to improve>
#      ---
#   4. If no issues found, output: NO_STYLE_ISSUES
#
# Input variables:
#   - {code}      → The source code
#   - {language}  → The programming language
#
# Example:
#   STYLE_QUALITY_PROMPT = PromptTemplate(
#       input_variables=["code", "language"],
#       template="""You are a code quality expert...
#       ...
#       """
#   )

STYLE_QUALITY_PROMPT = PromptTemplate(
    input_variables=["code", "language"],
    template="""
You are a code quality expert reviewing {language} code.

Analyze the code for style and quality issues including:
- Naming conventions
- Function length
- Code duplication
- Documentation
- Complexity
- Best practices

Code: {code}

For EACH issue found, output EXACTLY in this format:

ISSUE: <description>
CATEGORY: <naming|structure|complexity|best_practice>
LINE: <line number or "unknown">
SUGGESTION: <how to improve>
---

If no issues found, output:
NO_STYLE_ISSUES
"""
)

# ──────────────────────────────────────────────
# TODO 4: Concept Explainer Prompt Template
# ──────────────────────────────────────────────
# The Concept Explainer agent uses RAG to pull from
# CS documentation and explain *why* issues exist.
#
# Your prompt should instruct the LLM to:
#   1. Read the bug report and the student's code
#   2. For each bug, identify the underlying CS concept
#   3. Explain the concept clearly for a student
#   4. Provide a correct code example if possible
#   5. Output in this EXACT format per concept:
#      CONCEPT: <name of the concept>
#      EXPLANATION: <clear educational explanation>
#      RELATED_BUG: <which bug this relates to>
#      CODE_EXAMPLE: <correct code snippet or "none">
#      ---
#
# Input variables:
#   - {code}         → The source code
#   - {language}     → The programming language
#   - {bug_report}   → The bug report text
#   - {rag_context}  → Retrieved documentation from ChromaDB
#
# Tip: The {rag_context} comes from your RAG pipeline
# (ChromaDB retrieval). Tell the LLM to use it as
# reference material for explanations.

CONCEPT_EXPLAINER_PROMPT = PromptTemplate(
    input_variables=["code", "language", "bug_report", "rag_context"],
    template="""
You are a computer science tutor.
Use the provided documentation context to explain concepts clearly.

RAG Context: {rag_context}
Code ({language}): {code}
Bug Report:{bug_report}

For each bug, identify the underlying concept and explain it.

Output EXACTLY in this format:

CONCEPT: <concept name>
EXPLANATION: <clear explanation>
RELATED_BUG: <bug description>
CODE_EXAMPLE: <correct code or "none">
---

Be clear, simple and educational.
"""
)

# ──────────────────────────────────────────────
# TODO 5: Challenge Generator Prompt Template
# ──────────────────────────────────────────────
# The Challenge Generator creates follow-up coding
# exercises based on the student's weak spots.
#
# Your prompt should instruct the LLM to:
#   1. Read the bug report and style issues
#   2. Identify 1-3 weak areas the student needs practice in
#   3. Create a coding challenge for each weak area
#   4. Output in this EXACT format per challenge:
#      TITLE: <challenge name>
#      DESCRIPTION: <what the student needs to do>
#      DIFFICULTY: <easy|medium|hard>
#      STARTER_CODE: <code template, use \\n for newlines>
#      HINT: <a helpful hint, or "none">
#      ---
#
# Input variables:
#   - {language}     → The programming language
#   - {bug_report}   → Bugs found in the student's code
#   - {style_report} → Style issues found
#
# Tip: Challenges should be focused and educational.
# Each should target a specific weakness found in the review.

CHALLENGE_GENERATOR_PROMPT = PromptTemplate(
    input_variables=["language", "bug_report", "style_report"],
    template="""
You are a coding mentor.
Based on the student's weaknesses, generate 1-3 coding challenges.

Language: {language}
Bug Report: {bug_report}
Style Issues: {style_report}

For EACH challenge, output EXACTLY:

TITLE: <challenge name>
DESCRIPTION: <task description>
DIFFICULTY: <easy|medium|hard>
STARTER_CODE: <code template using \\n for newlines>
HINT: <hint or "none">
---

Make challenges focused and educational.
"""
)


# ──────────────────────────────────────────────
# TODO 6: Transcript Parser Prompt Template
# ──────────────────────────────────────────────
# The Transcript Parser extracts code and context from
# a voice transcription. When a student speaks their code
# aloud (via the /review-voice endpoint), the audio is
# first transcribed to text, then this prompt extracts
# the actual code and any context.
#
# Your prompt should instruct the LLM to:
#   1. Read the raw transcript of a student speaking
#   2. Extract the code they described/dictated
#   3. Extract any additional context they mentioned
#   4. Output in this EXACT format:
#      CODE: <the extracted code, properly formatted>
#      CONTEXT: <any context the student mentioned, or "none">
#
# Input variables:
#   - {transcript} → The raw text transcription of the audio
#   - {language}   → The programming language the student specified
#
# Tips:
#   - Students may say things like "def add open paren a comma b"
#     → You need to convert this to: def add(a, b)
#   - They may include context like "this is supposed to sort a list"
#     → Extract that as the CONTEXT
#   - Handle common speech-to-code patterns:
#     "open paren" → (, "close paren" → )
#     "colon" → :, "equals" → =, "indent" → proper indentation
#
# Example:
#   TRANSCRIPT_PARSER_PROMPT = PromptTemplate(
#       input_variables=["transcript", "language"],
#       template="""You are an expert at converting spoken
#       code descriptions into actual code...
#       ...
#       CODE: <extracted code>
#       CONTEXT: <extracted context or "none">"""
#   )

TRANSCRIPT_PARSER_PROMPT = PromptTemplate(
    input_variables=["transcript", "language"],
    template="""
You are an expert at converting spoken programming descriptions into correctly formatted code.

Language: {language}
Transcript: {transcript}

Your task:
1. Convert spoken phrases into valid code syntax
2. Fix formatting and indentation
3. Extract any additional context mentioned by the student

Common speech-to-code patterns (not exhaustive, generalize intelligently):
- "open parenthesis" → (
- "close parenthesis" → )
- "open bracket" → [
- "close bracket" → ]
- "open brace" → {{
- "close brace" → }}
- "colon" → :
- "comma" → ,
- "dot" → .
- "equals" / "equal to" → =
- "double equals" → ==
- "not equal" → !=
- "greater than" → >
- "less than" → <
- "greater than or equal to" → >=
- "less than or equal to" → <=
- "plus" → +
- "minus" → -
- "times" / "multiply" → *
- "divide" → /
- "modulo" → %
- "underscore" → _
- "newline" → new line
- "indent" → increase indentation level
- "dedent" → decrease indentation level
- "quote" / "double quote" → " "
- "single quote" → ' '

Also handle:
- Function definitions (e.g., "define function add")
- Loops ("for each", "while")
- Conditionals ("if", "else if", "else")
- Return statements
- Variable assignments
- Lists, dictionaries, and indexing
- Basic data structures and control flow

Be flexible, students may not speak perfectly.

Context extraction:
- If the student explains what the code does (e.g., "this function sorts a list"),
  extract it as CONTEXT.
- If no context is present, return "none".

Output EXACTLY in this format:

CODE: <clean, properly formatted code>
CONTEXT: <extracted context or "none">
"""
)