"""
CodeSensei — Pydantic Schemas (Data Models)
=============================================
Define the data structures used for request/response validation.

Concepts used:
- Pydantic BaseModel for data validation
- Type hints and field descriptions
- Nested models

═══════════════════════════════════════════════
  PART 1 (Eval 2) — YOUR TASKS:
    TODO 1: Define the CodeReviewRequest model
    TODO 2: Define the BugReport model
    TODO 3: Define the ReviewResponse model

  PART 2 (Capstone Extension) — YOUR TASKS:
    TODO 4: Define the StyleIssue model
    TODO 5: Define the ConceptExplanation model
    TODO 6: Define the CodingChallenge model
    TODO 7: Define the FullReviewResponse model
    TODO 8: Define the VoiceReviewRequest model
═══════════════════════════════════════════════
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


# ──────────────────────────────────────────────
# Enums (Provided)
# ──────────────────────────────────────────────

class Severity(str, Enum):
    """Bug severity levels."""
    CRITICAL = "critical"   # App crashes, security vulnerability
    HIGH = "high"           # Logic error, incorrect output
    MEDIUM = "medium"       # Poor practice, potential bug
    LOW = "low"             # Style issue, minor improvement


class Language(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"


# ╔═══════════════════════════════════════════════╗
# ║            PART 1 — Eval 2 TODOs              ║
# ╚═══════════════════════════════════════════════╝


# ──────────────────────────────────────────────
# TODO 1: Define the CodeReviewRequest model
# ──────────────────────────────────────────────
# This model represents the incoming request from
# a student who wants their code reviewed.
#
# Required fields:
#   - code (str): The source code to review
#       → Must not be empty
#       → Hint: use Field(min_length=1) for validation
#   - language (Language): Programming language of the code
#       → Use the Language enum defined above
#
# Optional fields:
#   - context (str): Additional context about the code
#       → e.g., "This is a sorting algorithm"
#       → Default to None
#
# Example usage:
#   request = CodeReviewRequest(
#       code="def add(a, b): return a - b",
#       language=Language.PYTHON,
#       context="Simple addition function"
#   )

class CodeReviewRequest(BaseModel):
    code:str = Field(..., min_length=1)
    language:Language
    context:Optional[str] = None


# ──────────────────────────────────────────────
# TODO 2: Define the BugReport model
# ──────────────────────────────────────────────
# This model represents a single bug found in the code.
#
# Required fields:
#   - bug_description (str): What the bug is
#       → Use Field(..., description="...") for documentation
#   - severity (Severity): How critical is this bug
#       → Use the Severity enum defined above
#   - suggestion (str): How to fix the bug
#
# Optional fields:
#   - line_number (int): Which line has the bug
#       → Default to None (some bugs are structural)
#
# Example usage:
#   bug = BugReport(
#       bug_description="Division by zero possible",
#       severity=Severity.CRITICAL,
#       suggestion="Add a check for zero denominator",
#       line_number=5
#   )

class BugReport(BaseModel):
    bug_description: str = Field(..., min_length=1)
    severity: Severity
    suggestion: str = Field(..., min_length=1)
    line_number: Optional[int] = None
    
# ──────────────────────────────────────────────
# TODO 3: Define the ReviewResponse model
# ──────────────────────────────────────────────
# This model represents the complete review sent back
# to the student.
#
# Required fields:
#   - bugs (List[BugReport]): List of bugs found
#       → Use Field(default_factory=list) for empty default
#   - summary (str): Overall review summary (2-3 sentences)
#   - score (int): Code quality score from 0-100
#       → Use Field(..., ge=0, le=100) for validation
#
# Optional fields:
#   - language (Language): The language that was reviewed
#       → Default to None
#
# Example usage:
#   response = ReviewResponse(
#       bugs=[bug1, bug2],
#       summary="Found 2 bugs...",
#       score=65,
#       language=Language.PYTHON
#   )

class ReviewResponse(BaseModel):
    summary: str = Field(..., min_length=1)
    score: int = Field(..., ge=0, le=100)
    bugs: List[BugReport] = Field(default_factory=list)
    language: Optional[Language] = None


# ╔═══════════════════════════════════════════════╗
# ║       PART 2 — Capstone Extension TODOs        ║
# ╚═══════════════════════════════════════════════╝
# Complete these AFTER finishing Part 1.
# These extend CodeSensei with additional agents
# and Voice-to-Text input.


# ──────────────────────────────────────────────
# TODO 4: Define the StyleIssue model
# ──────────────────────────────────────────────
# Used by the Style & Quality Agent to report
# code style and best-practice issues.
#
# Required fields:
#   - issue (str): Description of the style issue
#       → e.g., "Variable name 'x' is not descriptive"
#   - category (str): Category of the issue
#       → e.g., "naming", "structure", "complexity", "best_practice"
#   - suggestion (str): How to improve
#
# Optional fields:
#   - line_number (int): Where the issue is (default None)
#
# Example usage:
#   issue = StyleIssue(
#       issue="Function is too long (45 lines)",
#       category="complexity",
#       suggestion="Break into smaller helper functions",
#       line_number=10
#   )

class StyleIssue(BaseModel):
        issue: str = Field (..., min_length=1)
        category: str = Field(..., min_length=1)
        suggestion: str = Field(..., min_length=1)
        line_number: Optional[int] = None

# ──────────────────────────────────────────────
# TODO 5: Define the ConceptExplanation model
# ──────────────────────────────────────────────
# Used by the RAG-powered Concept Explainer Agent
# to teach the student *why* something is an issue.
#
# Required fields:
#   - concept (str): The CS concept being explained
#       → e.g., "Off-by-one error", "Null safety"
#   - explanation (str): Clear educational explanation
#   - related_bug (str): Which bug this relates to
#
# Optional fields:
#   - resource_link (str): Link to further reading (default None)
#   - code_example (str): A correct code example (default None)
#
# Example usage:
#   explanation = ConceptExplanation(
#       concept="Off-by-one error",
#       explanation="An off-by-one error occurs when...",
#       related_bug="Loop iterates one too many times",
#       code_example="for i in range(len(arr)):  # correct"
#   )

class ConceptExplanation(BaseModel):
        concept: str = Field(..., min_length=1)
        explanation: str = Field(..., min_length=1)
        related_bug: str = Field(..., min_length=1)
        resource_link: Optional[str] = None
        code_example: Optional[str] = None

# ──────────────────────────────────────────────
# TODO 6: Define the CodingChallenge model
# ──────────────────────────────────────────────
# Used by the Challenge Generator Agent to create
# follow-up exercises based on the student's weak spots.
#
# Required fields:
#   - title (str): Name of the challenge
#       → e.g., "Fix the Edge Cases"
#   - description (str): What the student needs to do
#   - difficulty (str): "easy", "medium", or "hard"
#   - starter_code (str): Code template to start from
#
# Optional fields:
#   - hint (str): A helpful hint (default None)
#
# Example usage:
#   challenge = CodingChallenge(
#       title="Handle Empty Input",
#       description="Modify the function to handle empty lists",
#       difficulty="easy",
#       starter_code="def find_max(numbers):\n    # your code here",
#       hint="What should the function return for []?"
#   )

class CodingChallenge(BaseModel):
        title: str = Field(..., min_length=1)
        description: str = Field(..., min_length=1)
        difficulty: str = Field(..., min_length=1)
        starter_code: str = Field(..., min_length=1)
        hint: Optional[str] = None

# ──────────────────────────────────────────────
# TODO 7: Define the FullReviewResponse model
# ──────────────────────────────────────────────
# Extended response that includes output from ALL agents.
# This is returned by the /review-code-advanced endpoint.
#
# Required fields:
#   - bugs (List[BugReport]): From Bug Detector agent
#   - style_issues (List[StyleIssue]): From Style & Quality agent
#   - explanations (List[ConceptExplanation]): From Concept Explainer
#   - challenges (List[CodingChallenge]): From Challenge Generator
#   - summary (str): Overall coordinator summary
#   - score (int): 0-100, validated with ge=0, le=100
#
# Optional fields:
#   - language (Language): Language reviewed (default None)
#   - reasoning_trace (str): The ReAct agent's reasoning log
#       → Shows the agent's thought process (default None)
#
# Hint: Use Field(default_factory=list) for all list fields

class FullReviewResponse(BaseModel):
    summary: str = Field(..., min_length=1)
    score: int = Field(..., ge=0, le=100)
    bugs: List[BugReport] = Field(default_factory=list)
    style_issues: List[StyleIssue] = Field(default_factory=list)
    explanations: List[ConceptExplanation] = Field(default_factory=list)
    challenges: List[CodingChallenge] = Field(default_factory=list)
    language: Optional[Language] = None
    reasoning_trace: Optional[str] = None

# ──────────────────────────────────────────────
# TODO 8: Define the VoiceReviewRequest model
# ──────────────────────────────────────────────
# This model is used for the /review-voice endpoint.
# Note: The actual file upload is handled by FastAPI's
# UploadFile — this model captures the additional
# metadata sent alongside the audio file.
#
# Required fields:
#   - language (Language): Programming language of the code
#       → The student says what language their code is in
#
# Optional fields:
#   - context (str): Additional context (default None)
#   - use_advanced (bool): Whether to use the full
#       multi-agent review (default False)
#       → False = basic review (Part 1 coordinator)
#       → True = advanced review (Part 2 ReAct coordinator)
#
# Example usage:
#   metadata = VoiceReviewRequest(
#       language=Language.PYTHON,
#       context="This is a sorting function",
#       use_advanced=True
#   )

class VoiceReviewRequest(BaseModel):
    context: Optional[str] = None
    use_advanced: bool = False
    language: Language
