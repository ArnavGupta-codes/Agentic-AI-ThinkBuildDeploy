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
from app.schemas import BugReport, ReviewResponse, Severity


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

# ╔═══════════════════════════════════════════════╗
# ║       PART 2 — Capstone Extension TODOs       ║
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

def parse_style_report(raw_output: str) -> List[StyleIssue]:
    issues = []

    if "NO_STYLE_ISSUES" in raw_output:
        return []

    blocks = raw_output.split("---")

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        issue_text = ""
        category = ""
        line_number = None
        suggestion = ""

        lines = block.split("\n")

        for line in lines:
            line = line.strip()

            if line.startswith("ISSUE:"):
                issue_text = line.replace("ISSUE:", "").strip()

            elif line.startswith("CATEGORY:"):
                category = line.replace("CATEGORY:", "").strip()

            elif line.startswith("LINE:"):
                value = line.replace("LINE:", "").strip()
                if value.lower() != "unknown":
                    try:
                        line_number = int(value)
                    except:
                        line_number = None

            elif line.startswith("SUGGESTION:"):
                suggestion = line.replace("SUGGESTION:", "").strip()

        issues.append(
            StyleIssue(
                issue=issue_text,
                category=category,
                suggestion=suggestion,
                line_number=line_number
            )
        )

    return issues


def run_style_quality(code: str, language: str) -> List[StyleIssue]:
    chain = STYLE_QUALITY_PROMPT | llm

    result = chain.invoke({
        "code": code,
        "language": language
    })

    raw_output = result.content

    issues = parse_style_report(raw_output)
    return issues

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

def run_concept_explainer(
    code: str, language: str, bug_report: str
) -> List[ConceptExplanation]:
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer

        embed_model = SentenceTransformer("intfloat/e5-base-v2")
        client = chromadb.PersistentClient(path="./RAG_db")
        collection = client.get_collection(name="RAG_db")

        query_embedding = embed_model.encode(bug_report).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=4
        )
        relevant_chunks = results["documents"][0]
        rag_context = "\n".join(relevant_chunks) if relevant_chunks else "No documentation available"
    except Exception:
        rag_context = "No documentation available"

    chain = CONCEPT_EXPLAINER_PROMPT | llm

    result = chain.invoke({
        "code": code,
        "language": language,
        "bug_report": bug_report,
        "rag_context": rag_context,
    })

    raw_output = result.content

    explanations = []
    blocks = raw_output.split("---")

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        concept = ""
        explanation = ""
        related_bug = ""
        code_example = None

        lines = block.split("\n")
        for line in lines:
            line = line.strip()

            if line.startswith("CONCEPT:"):
                concept = line.replace("CONCEPT:", "").strip()
            elif line.startswith("EXPLANATION:"):
                explanation = line.replace("EXPLANATION:", "").strip()
            elif line.startswith("RELATED_BUG:"):
                related_bug = line.replace("RELATED_BUG:", "").strip()
            elif line.startswith("CODE_EXAMPLE:"):
                val = line.replace("CODE_EXAMPLE:", "").strip()
                code_example = None if val.lower() == "none" else val

        if concept and explanation and related_bug:
            try:
                explanations.append(ConceptExplanation(
                    concept=concept,
                    explanation=explanation,
                    related_bug=related_bug,
                    code_example=code_example,
                ))
            except Exception:
                continue

    return explanations



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
        "style_report": style_report,
    })

    raw_output = result.content

    challenges = []
    blocks = raw_output.split("---")

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        title = ""
        description = ""
        difficulty = ""
        starter_code = ""
        hint = None

        lines = block.split("\n")
        for line in lines:
            line = line.strip()

            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
            elif line.startswith("DESCRIPTION:"):
                description = line.replace("DESCRIPTION:", "").strip()
            elif line.startswith("DIFFICULTY:"):
                difficulty = line.replace("DIFFICULTY:", "").strip()
            elif line.startswith("STARTER_CODE:"):
                val = line.replace("STARTER_CODE:", "").strip()
                starter_code = val.replace("\\n", "\n")
            elif line.startswith("HINT:"):
                val = line.replace("HINT:", "").strip()
                hint = None if val.lower() == "none" else val

        if title and description and difficulty and starter_code:
            try:
                challenges.append(CodingChallenge(
                    title=title,
                    description=description,
                    difficulty=difficulty,
                    starter_code=starter_code,
                    hint=hint,
                ))
            except Exception:
                continue

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

def run_react_coordinator(
    code: str, language: str, context: str = ""
) -> FullReviewResponse:
    from app.tools import get_all_tools
    from langchain.agents import create_react_agent, AgentExecutor
    from langchain.prompts import PromptTemplate

    tools = get_all_tools()

    # Define the ReAct prompt
    react_prompt = PromptTemplate.from_template("""You are CodeSensei, an AI code reviewer and programming tutor.
Review student code by calling tools in this order:
1. BugDetector  - find bugs
2. StyleQuality - check style and best practices
3. ConceptExplainer - explain the CS concepts behind the bugs
4. ChallengeGenerator - create targeted practice challenges

You have access to the following tools: {tools}

Use the following format strictly:
Thought: think about what to do next
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I have completed all four reviews
Final Answer: Code review complete.

Begin!

Question: {input}
Thought:{agent_scratchpad}""")

    # Create the ReAct agent and executor
    agent = create_react_agent(llm, tools, react_prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        max_iterations=10,
    )

    # Run the executor
    formatted_input = (
        f"Review this {language} code:\n```\n{code}\n```\n"
        f"Context: {context or 'No additional context'}\n"
        #f"Tool input format — BugDetector/StyleQuality: '{language}|||{code}'"
    )

    # Run executor for the reasoning trace only; ignore errors
    reasoning_trace = None
    # try:
    #     exec_result = executor.invoke({"input": formatted_input})
    #     intermediate_steps = exec_result.get("intermediate_steps", [])
    #     reasoning_parts = []
    #     for action, observation in intermediate_steps:
    #         reasoning_parts.append(
    #             f"{action.log.strip()}\nObservation: {observation}"
    #         )
    #     reasoning_trace = "\n\n".join(reasoning_parts) if reasoning_parts else None
    # except Exception:
    #     pass

    # Call each agent once to get typed objects
    bugs = run_bug_detector(code, language)

    bug_report_text = "\n".join([
        f"Bug {i+1}: {b.bug_description} (Severity: {b.severity.value})"
        for i, b in enumerate(bugs)
    ]) if bugs else "No bugs found."

    style_issues = run_style_quality(code, language)

    style_report_text = "\n".join([
        f"Issue {i+1}: {s.issue} (Category: {s.category})"
        for i, s in enumerate(style_issues)
    ]) if style_issues else "No style issues."

    explanations = run_concept_explainer(code, language, bug_report_text)
    challenges = run_challenge_generator(language, bug_report_text, style_report_text)

    # Get summary + score without re-running bug detection
    summary = "Review complete."
    score = 50
    try:
        coord_chain = COORDINATOR_PROMPT | llm
        coord_result = coord_chain.invoke({
            "code": code,
            "language": language,
            "bug_report": bug_report_text,
            "context": context or "No additional context",
        })
        for line in coord_result.content.split("\n"):
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("SCORE:"):
                try:
                    score = max(0, min(100, int(line.replace("SCORE:", "").strip())))
                except ValueError:
                    pass
    except Exception:
        pass

    # Build and return the FullReviewResponse
    return FullReviewResponse(
        bugs=bugs,
        style_issues=style_issues,
        explanations=explanations,
        challenges=challenges,
        summary=summary,
        score=score,
        language=language,
        reasoning_trace=reasoning_trace,
    )