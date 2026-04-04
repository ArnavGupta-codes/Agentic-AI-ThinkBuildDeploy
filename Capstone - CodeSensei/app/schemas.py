"""
CodeSensei — Pydantic Schemas (Data Models)
=============================================
Define the data structures used for request/response validation.

Concepts used:
- Pydantic BaseModel for data validation
- Type hints and field descriptions
- Nested models

YOUR TASKS:
  TODO 1: Define the CodeReviewRequest model
  TODO 2: Define the BugReport model
  TODO 3: Define the ReviewResponse model
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
    # TODO: Define the fields described above
    # Hint: Use Field(...) for required fields with constraints
    #       Use Optional[str] = None for optional fields
    code: str = Field(..., min_length=1)
    language: Language
    context: Optional[str] = None


# ──────────────────────────────────────────────
# TODO 2: Define the BugReport model
# ──────────────────────────────────────────────
# This model represents a single bug found by the
# Bug Detector agent.
#
# Required fields:
#   - bug_description (str): What the bug is
#       → e.g., "Using subtraction instead of addition"
#   - severity (Severity): How critical is this bug
#       → Use the Severity enum defined above
#   - suggestion (str): How to fix the bug
#       → e.g., "Change 'return a - b' to 'return a + b'"
#
# Optional fields:
#   - line_number (int): Which line the bug is on
#       → Default to None (not always determinable)
#
# Example usage:
#   bug = BugReport(
#       bug_description="Subtraction used instead of addition",
#       severity=Severity.HIGH,
#       suggestion="Replace '-' with '+'",
#       line_number=2
#   )

class BugReport(BaseModel):
    # TODO: Define the fields described above
    bug_description: str
    severity: Severity
    suggestion: str
    line_number: Optional[int] = None


# ──────────────────────────────────────────────
# TODO 3: Define the ReviewResponse model
# ──────────────────────────────────────────────
# This model represents the complete review response
# sent back to the student.
#
# Required fields:
#   - bugs (List[BugReport]): List of bugs found
#       → Can be empty if code is bug-free
#       → Default to empty list
#   - summary (str): Overall review summary
#       → e.g., "Found 2 bugs: 1 high severity, 1 low severity"
#   - score (int): Code quality score from 0-100
#       → Use Field(ge=0, le=100) for validation
#
# Optional fields:
#   - language (str): The language that was reviewed
#       → Default to None
#
# Example usage:
#   response = ReviewResponse(
#       bugs=[bug1, bug2],
#       summary="Found 2 bugs in your Python code.",
#       score=65,
#       language="python"
#   )

class ReviewResponse(BaseModel):
    # TODO: Define the fields described above
    # Hint: Use Field(default_factory=list) for mutable defaults
    #       Use Field(ge=0, le=100) for bounded integers
    bugs: List[BugReport] = Field(default_factory=list)
    summary: str
    score: int = Field(..., ge=0, le=100)
    language: Optional[str] = None
