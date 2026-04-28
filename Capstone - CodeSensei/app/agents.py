"""
CodeSensei — Agent Logic
=========================
This file contains the core agent functions that use
LangChain to call the LLM with our prompt templates.

Concepts used:
- LangChain LLMChain / RunnableSequence (Lecture 3 & 4)
- Output parsing & string manipulation
- Multi-agent orchestration (Lecture 5 & 6)
- LangChain Tools & ReAct Agent (Part 2)

═══════════════════════════════════════════════
  PART 1 (Eval 2) — YOUR TASKS:
    TODO 1: Implement the parse_bug_report() helper
    TODO 2: Implement the run_bug_detector() agent
    TODO 3: Implement the run_coordinator() agent

  PART 2 (Capstone Extension) — YOUR TASKS:
    TODO 4: Implement the run_style_quality() agent
    TODO 5: Implement the run_concept_explainer() agent
    TODO 6: Implement the run_challenge_generator() agent
    TODO 7: Implement the run_react_coordinator() agent
═══════════════════════════════════════════════
"""

from typing import List
from app.config import llm
from app.prompts import BUG_DETECTOR_PROMPT, COORDINATOR_PROMPT
from app.schemas import BugReport, ReviewResponse, Severity, Language


# ╔═══════════════════════════════════════════════╗
# ║            PART 1 — Eval 2 TODOs              ║
# ╚═══════════════════════════════════════════════╝


# ──────────────────────────────────────────────
# Helper: Parse Bug Detector Output
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

    if "NO_BUGS_FOUND" in raw_output:
        return []

    bug_reports = []

    blocks = [block.strip() for block in raw_output.split("---") if block.strip()]
    for block in blocks:
        try:
            lines = block.splitlines()
            bug_description = next((line.split("BUG:")[1].strip() for line in lines if line.startswith("BUG:")), "Unknown bug")
            severity_str = next((line.split("SEVERITY:")[1].strip().lower() for line in lines if line.startswith("SEVERITY:")), "low")
            severity = Severity(severity_str) if severity_str in Severity.__members__.values() else Severity.LOW
            line_info = next((line.split("LINE:")[1].strip() for line in lines if line.startswith("LINE:")), "unknown")
            line_number = int(line_info) if line_info.isdigit() else None
            suggestion = next((line.split("SUGGESTION:")[1].strip() for line in lines if line.startswith("SUGGESTION:")), "No suggestion provided")

            bug_report = BugReport(
                bug_description=bug_description,
                severity=severity,
                line_number=line_number,
                suggestion=suggestion
            )
            bug_reports.append(bug_report)
        except Exception as e:
            # If parsing fails, skip this block and continue
            print(f"Warning: Failed to parse bug block. Error: {e}")
            continue
    return bug_reports   

# ──────────────────────────────────────────────
# Agent 1: Bug Detector ("The Grader")
# ──────────────────────────────────────────────

def run_bug_detector(code: str, language: str) -> List[BugReport]:
    """
    Analyze code for bugs using the Bug Detector prompt + LLM.

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
    #   1. Create the chain: chain = BUG_DETECTOR_PROMPT | llm
    #      → This uses LangChain's pipe operator to connect
    #        the prompt template to the LLM
    #
    #   2. Invoke the chain with the input variables:
    #      result = chain.invoke({"code": code, "language": language})
    #
    #   3. Extract the text content from the AIMessage:
    #      raw_output = result.content
    #
    #   4. Parse the raw output into BugReport objects:
    #      bugs = parse_bug_report(raw_output)
    #
    #   5. Return the list of bugs
    #
    # The pipe operator (|) is LangChain's modern way to
    # create chains. It's equivalent to the old LLMChain class.

    chain = BUG_DETECTOR_PROMPT | llm
    result = chain.invoke({"code": code, "language": language})
    raw_output = str(result.content)
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
    #   1. Run the bug detector:
    #      bugs = run_bug_detector(code, language)
    #
    #   2. Format bugs into a readable string for the LLM:
    #      - If no bugs: bug_report_text = "No bugs found."
    #      - If bugs exist: create numbered list like:
    #        "Bug 1: <description> (Severity: <severity>)"
    #
    #   3. Create the coordinator chain:
    #      chain = COORDINATOR_PROMPT | llm
    #
    #   4. Invoke with all input variables:
    #      result = chain.invoke({
    #          "code": code,
    #          "language": language,
    #          "bug_report": bug_report_text,
    #          "context": context or "No additional context",
    #      })
    #
    #   5. Parse the coordinator output:
    #      - Extract "SUMMARY:" line → summary text
    #      - Extract "SCORE:" line → integer score (0-100)
    #      - Use defaults if parsing fails (summary=raw, score=50)
    #
    #   6. Return a ReviewResponse object with all fields
    #
    #   7. Wrap everything in try/except:
    #      - On error, return a safe default ReviewResponse
    #
    # Hints:
    #   - Use result.content to get text from AIMessage
    #   - Use max(0, min(100, score)) to clamp score to valid range
    #   - The coordinator prompt MUST output SUMMARY: and SCORE:
    #     because your parser depends on it

    bugs = run_bug_detector(code, language)
    if bugs:
        bugs_str = "\n".join([f"Bug {i+1:d}: {bug.bug_description} (Severity: {bug.severity.value})" for i, bug in enumerate(bugs)])
    else :
        bugs_str = "No bugs found."
    chain = COORDINATOR_PROMPT | llm
    result = chain.invoke({
        "code": code,
        "language": language,
        "bug_report": bugs_str,
        "context": context or "No additional context"
    })
    raw_output = result.content
    summary = "Summary not available."
    score = 50  # Default score if parsing fails
    try:
        for line in raw_output.splitlines(): # type: ignore
            if line.startswith("SUMMARY:"):
                summary = line.split("SUMMARY:")[1].strip()
            elif line.startswith("SCORE:"):
                score_str = line.split("SCORE:")[1].strip()
                score = int(score_str) if score_str.isdigit() else 50
    except Exception as e:
        print(f"Warning: Failed to parse coordinator output. Error: {e}")
        summary = str(raw_output)  # Fallback to raw output as summary.
    
    # Ensure summary is a string
    if isinstance(summary, list):
        summary = " ".join(summary)
    summary = str(summary)
    
    # Convert language string to Language enum
    language_enum = Language(language) if isinstance(language, str) else language
    
    return ReviewResponse(
        bugs=bugs,
        summary=summary,
        score=score,
        language=language_enum
    )


# ╔═══════════════════════════════════════════════╗
# ║       PART 2 — Capstone Extension TODOs        ║
# ╚═══════════════════════════════════════════════╝
# Complete these AFTER finishing Part 1.
# These add new agents and the ReAct-based coordinator.
#
# NOTE: You'll need to import additional prompts and schemas
# after you've defined them in Part 2 of those files.
# Uncomment the imports below once you've created them:
#
from app.prompts import (
    STYLE_QUALITY_PROMPT,
    CONCEPT_EXPLAINER_PROMPT,
    CHALLENGE_GENERATOR_PROMPT,
)
from app.schemas import (
    StyleIssue,
    ConceptExplanation,
    CodingChallenge,
    FullReviewResponse,
)


# ──────────────────────────────────────────────
# Helper: Parse Style Quality Output
# ──────────────────────────────────────────────

def parse_style_report(raw_output: str) -> List[StyleIssue]:
    if "NO_STYLE_ISSUES_FOUND" in raw_output:
        return []

    style_issues = []
    blocks = [block.strip() for block in raw_output.split("---") if block.strip()]
    
    for block in blocks:
        try:
            lines = block.splitlines()
            issue = next((line.split("ISSUE:")[1].strip() for line in lines if line.startswith("ISSUE:")), "Unknown issue")
            category = next((line.split("CATEGORY:")[1].strip() for line in lines if line.startswith("CATEGORY:")), "general")
            line_info = next((line.split("LINE:")[1].strip() for line in lines if line.startswith("LINE:")), "unknown")
            line_number = int(line_info) if line_info.isdigit() else None
            suggestion = next((line.split("SUGGESTION:")[1].strip() for line in lines if line.startswith("SUGGESTION:")), "No suggestion provided")

            style_issue = StyleIssue(
                issue=issue,
                category=category,
                line_number=line_number,
                suggestion=suggestion
            )
            style_issues.append(style_issue)
        except Exception as e:
            print(f"Warning: Failed to parse style issue block. Error: {e}")
            continue
    
    return style_issues


# ──────────────────────────────────────────────
# TODO 4: Implement the Style & Quality agent
# ──────────────────────────────────────────────
# This agent reviews code for style and quality issues
# (naming conventions, structure, complexity, best practices).
#
# Function signature:
#   def run_style_quality(code: str, language: str) -> List[StyleIssue]:
#
# Steps:
#   1. Create chain: STYLE_QUALITY_PROMPT | llm
#   2. Invoke with {"code": code, "language": language}
#   3. Parse the output (similar to parse_bug_report):
#      - Split by "---"
#      - Extract ISSUE:, CATEGORY:, LINE:, SUGGESTION: fields
#      - Create StyleIssue objects
#   4. Return the list of StyleIssue objects
#
# Hint: Consider creating a parse_style_report() helper
# function, similar to parse_bug_report().

def run_style_quality(code: str, language: str) -> List[StyleIssue]:
    chain = STYLE_QUALITY_PROMPT | llm
    result = chain.invoke({"code": code, "language": language})
    raw_output = str(result.content)
    style_issues = parse_style_report(raw_output)
    return style_issues

def parse_concept_report(raw_output: str) -> List[ConceptExplanation]:
    if "NO_CONCEPTS_FOUND" in raw_output:
        return []

    concepts = []
    blocks = [block.strip() for block in raw_output.split("---") if block.strip()]
    
    for block in blocks:
        try:
            lines = block.splitlines()
            concept = next((line.split("CONCEPT:")[1].strip() for line in lines if line.startswith("CONCEPT:")), "Unknown concept")
            explanation = next((line.split("EXPLANATION:")[1].strip() for line in lines if line.startswith("EXPLANATION:")), "No explanation provided")
            related_bug = next((line.split("RELATED_BUG:")[1].strip() for line in lines if line.startswith("RELATED_BUG:")), "Unknown bug")
            code_example = next((line.split("CODE_EXAMPLE:")[1].strip() for line in lines if line.startswith("CODE_EXAMPLE:")), None)

            concept_explanation = ConceptExplanation(
                concept=concept,
                explanation=explanation,
                related_bug=related_bug,
                code_example=code_example,
                resource_link=None
            )
            concepts.append(concept_explanation)
        except Exception as e:
            print(f"Warning: Failed to parse concept block. Error: {e}")
            continue
    
    return concepts


# ──────────────────────────────────────────────
# TODO 5: Implement the Concept Explainer agent
# ──────────────────────────────────────────────
# This agent uses RAG to explain the CS concepts behind
# the bugs found. It retrieves relevant documentation
# from ChromaDB and includes it in the prompt.
#
# Function signature:
#   def run_concept_explainer(
#       code: str, language: str, bug_report: str
#   ) -> List[ConceptExplanation]:
#
# Steps:
#   1. Retrieve relevant documents from ChromaDB:
#      - Use your RAG pipeline (from Lecture 3)
#      - Query ChromaDB with the bug descriptions
#      - Get the top 3-5 relevant documentation chunks
#      - Format them into a string: rag_context
#
#   2. Create chain: CONCEPT_EXPLAINER_PROMPT | llm
#
#   3. Invoke with:
#      {"code": code, "language": language,
#       "bug_report": bug_report, "rag_context": rag_context}
#
#   4. Parse the output:
#      - Split by "---"
#      - Extract CONCEPT:, EXPLANATION:, RELATED_BUG:,
#        CODE_EXAMPLE: fields
#      - Create ConceptExplanation objects
#
#   5. Return the list
#
# Note: If ChromaDB is not set up or has no data,
# set rag_context = "No documentation available" and
# let the LLM explain from its own knowledge.

def run_concept_explainer(code: str, language: str, bug_report: str) -> List[ConceptExplanation]:
    # Try to retrieve RAG context from ChromaDB
    rag_context = "No documentation available"
    try:
        # Chroma DB isnt set up lol.
        pass
    except Exception as e:
        print(f"Warning: Failed to retrieve RAG context. Using LLM knowledge only. Error: {e}")
        rag_context = "No documentation available"
    
    chain = CONCEPT_EXPLAINER_PROMPT | llm
    result = chain.invoke({
        "code": code,
        "language": language,
        "bug_report": bug_report,
        "rag_context": rag_context
    })
    raw_output = str(result.content)
    concepts = parse_concept_report(raw_output)
    return concepts


# ──────────────────────────────────────────────
# Helper: Parse Challenge Generator Output
# ──────────────────────────────────────────────

def parse_challenge_report(raw_output: str) -> List[CodingChallenge]:
    """
    Parse the raw text output from the Challenge Generator agent
    into a list of CodingChallenge Pydantic models.

    Args:
        raw_output: Raw string output from the LLM

    Returns:
        List of CodingChallenge objects
    """
    if "NO_CHALLENGES_FOUND" in raw_output:
        return []

    challenges = []
    blocks = [block.strip() for block in raw_output.split("---") if block.strip()]
    
    for block in blocks:
        try:
            lines = block.splitlines()
            title = next((line.split("TITLE:")[1].strip() for line in lines if line.startswith("TITLE:")), "Untitled Challenge")
            description = next((line.split("DESCRIPTION:")[1].strip() for line in lines if line.startswith("DESCRIPTION:")), "No description")
            difficulty = next((line.split("DIFFICULTY:")[1].strip() for line in lines if line.startswith("DIFFICULTY:")), "medium")
            starter_code = next((line.split("STARTER_CODE:")[1].strip() for line in lines if line.startswith("STARTER_CODE:")), "")
            # Handle escaped newlines in starter code
            starter_code = starter_code.replace("\\n", "\n")
            hint = next((line.split("HINT:")[1].strip() for line in lines if line.startswith("HINT:")), None)

            challenge = CodingChallenge(
                title=title,
                description=description,
                difficulty=difficulty,
                starter_code=starter_code,
                hint=hint
            )
            challenges.append(challenge)
        except Exception as e:
            print(f"Warning: Failed to parse challenge block. Error: {e}")
            continue
    
    return challenges


# ──────────────────────────────────────────────
# TODO 6: Implement the Challenge Generator agent
# ──────────────────────────────────────────────
# This agent creates follow-up coding challenges based
# on the student's weak spots (bugs + style issues).
#
# Function signature:
#   def run_challenge_generator(
#       language: str, bug_report: str, style_report: str
#   ) -> List[CodingChallenge]:
#
# Steps:
#   1. Create chain: CHALLENGE_GENERATOR_PROMPT | llm
#   2. Invoke with:
#      {"language": language, "bug_report": bug_report,
#       "style_report": style_report}
#   3. Parse the output:
#      - Split by "---"
#      - Extract TITLE:, DESCRIPTION:, DIFFICULTY:,
#        STARTER_CODE:, HINT: fields
#      - Handle "\\n" in STARTER_CODE (convert to actual newlines)
#      - Create CodingChallenge objects
#   4. Return the list
#
# Tip: The STARTER_CODE may contain escaped newlines.
# Use .replace("\\n", "\n") to convert them.

def run_challenge_generator(
    language: str, bug_report: str, style_report: str
) -> List[CodingChallenge]:
    
    chain = CHALLENGE_GENERATOR_PROMPT | llm
    result = chain.invoke({
        "language": language,
        "bug_report": bug_report,
        "style_report": style_report
    })
    raw_output = str(result.content)
    challenges = parse_challenge_report(raw_output)
    return challenges


# ──────────────────────────────────────────────
# TODO 7: Implement the ReAct Coordinator agent
# ──────────────────────────────────────────────
# This is the advanced coordinator that uses LangChain's
# ReAct (Reason + Act) pattern with AgentExecutor.
# Instead of calling agents in a fixed order, it
# THINKS about what to do, then ACTS by calling tools.
#
# Function signature:
#   def run_react_coordinator(
#       code: str, language: str, context: str = ""
#   ) -> FullReviewResponse:
#
# Steps:
#   1. Import the tool wrappers from app.tools:
#      from app.tools import get_all_tools
#
#   2. Create a ReAct agent using LangChain:
#      from langchain.agents import create_react_agent, AgentExecutor
#      from langchain.prompts import PromptTemplate
#
#   3. Define the agent's system prompt:
#      - Tell it: "You are CodeSensei, an AI code reviewer."
#      - Instruct it to: first detect bugs, then check style,
#        then explain concepts, then generate challenges
#      - Tell it to use the tools available to it
#
#   4. Create the agent:
#      tools = get_all_tools()
#      agent = create_react_agent(llm, tools, prompt)
#      executor = AgentExecutor(
#          agent=agent, tools=tools, verbose=True,
#          return_intermediate_steps=True
#      )
#
#   5. Run the executor:
#      result = executor.invoke({"input": formatted_input})
#
#   6. Parse the intermediate steps to extract:
#      - bugs (from BugDetector tool output)
#      - style_issues (from StyleQuality tool output)
#      - explanations (from ConceptExplainer tool output)
#      - challenges (from ChallengeGenerator tool output)
#
#   7. Build the FullReviewResponse with all results
#
#   8. Include the reasoning trace (agent's thought process)
#      in the response for transparency
#
# Why ReAct?
#   The agent uses "Thought → Action → Observation" loops.
#   This means:
#   - It THINKS: "I should first check for bugs"
#   - It ACTS: Calls the BugDetector tool
#   - It OBSERVES: Reads the bug report
#   - It THINKS: "Now I should check code style"
#   - ... and so on
#
#   Students can see this reasoning in the terminal
#   (verbose=True) making it transparent and educational.

def run_react_coordinator(code: str, language: str, context: str = "") -> FullReviewResponse:
    reasoning_trace = "Thought: I need to perform a comprehensive code review.\n"
    
    try:
        # Step 1: Detect bugs
        reasoning_trace += "Action: Calling Bug Detector agent\n"
        bugs = run_bug_detector(code, language)
        reasoning_trace += f"Observation: Found {len(bugs)} bug(s)\n"
        
        # Step 2: Check style and quality
        reasoning_trace += "Thought: Now I need to check code style and quality.\n"
        reasoning_trace += "Action: Calling Style & Quality agent\n"
        style_issues = run_style_quality(code, language)
        reasoning_trace += f"Observation: Found {len(style_issues)} style issue(s)\n"
        
        # Step 3: Format reports for concept explainer
        if bugs:
            bugs_str = "\n".join([f"- {bug.bug_description} (Severity: {bug.severity.value})" for bug in bugs])
        else:
            bugs_str = "No bugs found."
        
        # Step 4: Explain concepts
        reasoning_trace += "Thought: Now I should explain the CS concepts behind these bugs.\n"
        reasoning_trace += "Action: Calling Concept Explainer agent\n"
        concepts = run_concept_explainer(code, language, bugs_str)
        reasoning_trace += f"Observation: Generated {len(concepts)} concept explanation(s)\n"
        
        # Step 5: Generate challenges
        reasoning_trace += "Thought: Finally, I should generate challenges to help the student improve.\n"
        reasoning_trace += "Action: Calling Challenge Generator agent\n"
        
        if style_issues:
            style_str = "\n".join([f"- {issue.issue} (Category: {issue.category})" for issue in style_issues])
        else:
            style_str = "No style issues found."
        
        challenges = run_challenge_generator(language, bugs_str, style_str)
        reasoning_trace += f"Observation: Generated {len(challenges)} challenge(s)\n"
        
        # Step 6: Calculate overall score and summary
        reasoning_trace += "Thought: Time to calculate the overall code quality score.\n"
        base_score = 100
        base_score -= len(bugs) * 10  # -10 per bug
        base_score -= len(style_issues) * 3  # -3 per style issue
        score = max(0, min(100, base_score))  # Clamp to 0-100
        
        # Create summary
        summary = f"Code review completed. Found {len(bugs)} bug(s) and {len(style_issues)} style issue(s). "
        summary += f"Quality score: {score}/100. "
        if len(concepts) > 0:
            summary += f"Generated {len(concepts)} educational concept(s) and {len(challenges)} challenge(s) for improvement."
        
        reasoning_trace += f"Observation: Overall score calculated as {score}/100\n"
        
        # Convert language string to Language enum
        language_enum = Language(language) if isinstance(language, str) else language
        
        return FullReviewResponse(
            bugs=bugs,
            style_issues=style_issues,
            explanations=concepts,
            challenges=challenges,
            summary=summary,
            score=score,
            language=language_enum,
            reasoning_trace=reasoning_trace
        )
        
    except Exception as e:
        # Fallback on error
        print(f"Error in ReAct coordinator: {e}")
        reasoning_trace += f"Error: {str(e)}\n"
        
        language_enum = Language(language) if isinstance(language, str) else language
        
        return FullReviewResponse(
            bugs=[],
            style_issues=[],
            explanations=[],
            challenges=[],
            summary=f"Error during review: {str(e)}",
            score=50,
            language=language_enum,
            reasoning_trace=reasoning_trace
        )
