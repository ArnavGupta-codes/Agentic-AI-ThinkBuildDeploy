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

BUG_DETECTOR_PROMPT = PromptTemplate (
       input_variables=["code", "language"],
       template="""You are a bug detection assistant. Your task is to anaylse the provided     
       Code ({language}): ```{code}``` and identify any bugs or issues. For each bug found, output in the following format:```
       BUG: <description of the bug>
       SEVERITY: <critical|high|medium|low>
       LINE: <line number or "unknown">
       SUGGESTION: <how to fix it>
       If no bugs found, output: NO_BUGS_FOUND
      
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

COORDINATOR_PROMPT = PromptTemplate (
       input_variables=["code", "language", "bug_report", "context"],
       template="""You are a Coordinator agent that takes the raw bug detector output
and creates a final, student-friendly review summary for the user. Summarize the bugs found in a helpful, educational tone.
Give an overall code quality score from 0-100. Output in this EXACT format:
SUMMARY: <a 2-3 sentence summary of the review>
SCORE: <number from 0-100>
Tips:
Be encouraging but honest
Score guide: 90-100 = excellent, 70-89 = good, 50-69 = needs work, <50 = significant issues
The summary should help the student LEARN, not just list errors       
       
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
       template="""You are a code quality expert who reviews code for style and best practices. Your task is to
       1. Analyze the {code} in the language {language} for style and quality issues
       2. Check for: naming conventions, function length,
          code duplication, proper documentation, complexity
       3. For EACH issue found, output in this EXACT format:
      ISSUE: <description of the style issue>
      CATEGORY: <naming|structure|complexity|best_practice>
      LINE: <line number or "unknown">
      SUGGESTION: <how to improve>
      ---
   4. If no issues found, output: NO_STYLE_ISSUES
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
       template="""You are a Concept Explainer agent who uses RAG to pull from
       CS documentation and explain *why* issues exist. Your task is to:
       1. Read the bug report and the student's {code} in the language {language}
       2. For each bug, identify the underlying CS concept
       3. Explain the concept clearly for a student
       4. Provide a correct code example if possible
       5. Output in this EXACT format per concept:
          CONCEPT: <name of the concept>
          EXPLANATION: <clear educational explanation>
          RELATED_BUG: <which bug this relates to>
          CODE_EXAMPLE: <correct code snippet or "none">
          ---
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
       template="""You are a code Challenge Generator who creates follow-up coding
# exercises based on the student's weak spots. Your task is to:
1. Read the bug report and style issues for a student's code in {language}
2. Identify 1-3 weak areas the student needs practice in
3. Create a coding challenge for each weak area
4. Output in this EXACT format per challenge:
   TITLE: <challenge name>
   DESCRIPTION: <what the student needs to do>
   DIFFICULTY: <easy|medium|hard>
   STARTER_CODE: <code template, use \\n for newlines>
   HINT: <a helpful hint, or "none">
   ---                
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
       input_variables=["language", "transcript"],
       template="""You are a transcript Parser that extracts code and context from a voice transcription. 

Your task:
1. Read this transcribed student speech in {language}: "{transcript}"
2. Extract the code they described/dictated
3. Extract any additional context they mentioned
4. Output in this EXACT format:
   CODE: <the extracted code, properly formatted>
   CONTEXT: <any context the student mentioned, or "none">

Tips:
   - Students may say things like "def add open paren a comma b"
     → Convert to: def add(a, b)
   - They may include context like "this is supposed to sort a list"
     → Extract that as the CONTEXT
   - Handle common speech-to-code patterns:
     "open paren" → (, "close paren" → )
     "colon" → :, "equals" → =, "indent" → proper indentation
      """
)
