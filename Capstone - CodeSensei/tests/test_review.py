"""
CodeSensei — Tests
===================
Run these tests to verify your implementations.

Usage:
    pytest tests/ -v

These tests validate:
1. Pydantic schemas accept valid data
2. Bug report parser works correctly
3. The /health endpoint responds
4. The /review-code endpoint works end-to-end (requires API key)
"""

import pytest
from fastapi.testclient import TestClient


# ──────────────────────────────────────────────
# Test 1: Schema Validation
# ──────────────────────────────────────────────
def test_code_review_request_valid():
    """Test that CodeReviewRequest accepts valid data."""
    from app.schemas import CodeReviewRequest, Language

    request = CodeReviewRequest(
        code="print('hello')",
        language=Language.PYTHON,
        context="Simple print statement"
    )
    assert request.code == "print('hello')"
    assert request.language == Language.PYTHON
    assert request.context == "Simple print statement"


def test_code_review_request_without_context():
    """Test that context is optional."""
    from app.schemas import CodeReviewRequest, Language

    request = CodeReviewRequest(
        code="console.log('hi')",
        language=Language.JAVASCRIPT,
    )
    assert request.context is None


def test_bug_report_creation():
    """Test that BugReport can be created with all fields."""
    from app.schemas import BugReport, Severity

    bug = BugReport(
        bug_description="Division by zero possible",
        severity=Severity.CRITICAL,
        suggestion="Add a check for zero denominator",
        line_number=5
    )
    assert bug.severity == Severity.CRITICAL
    assert bug.line_number == 5


def test_review_response_creation():
    """Test that ReviewResponse can be created."""
    from app.schemas import ReviewResponse, BugReport, Severity

    bug = BugReport(
        bug_description="Test bug",
        severity=Severity.LOW,
        suggestion="Fix it"
    )
    response = ReviewResponse(
        bugs=[bug],
        summary="Found 1 bug",
        score=85,
        language="python"
    )
    assert len(response.bugs) == 1
    assert response.score == 85


def test_review_response_score_bounds():
    """Test that score must be 0-100."""
    from app.schemas import ReviewResponse

    with pytest.raises(Exception):
        ReviewResponse(
            bugs=[],
            summary="Test",
            score=150  # Invalid! Should be 0-100
        )


# ──────────────────────────────────────────────
# Test 2: Bug Report Parser
# ──────────────────────────────────────────────
def test_parse_bug_report_no_bugs():
    """Test parser returns empty list for NO_BUGS_FOUND."""
    from app.agents import parse_bug_report

    result = parse_bug_report("NO_BUGS_FOUND")
    assert result == []


def test_parse_bug_report_single_bug():
    """Test parser correctly extracts a single bug."""
    from app.agents import parse_bug_report

    raw = """BUG: Using subtraction instead of addition
SEVERITY: high
LINE: 2
SUGGESTION: Change '-' to '+'
---"""
    result = parse_bug_report(raw)
    assert len(result) == 1
    assert "subtraction" in result[0].bug_description.lower()


def test_parse_bug_report_multiple_bugs():
    """Test parser handles multiple bugs."""
    from app.agents import parse_bug_report

    raw = """BUG: First bug
SEVERITY: high
LINE: 1
SUGGESTION: Fix first
---
BUG: Second bug
SEVERITY: low
LINE: 5
SUGGESTION: Fix second
---"""
    result = parse_bug_report(raw)
    assert len(result) == 2


# ──────────────────────────────────────────────
# Test 3: FastAPI Health Check
# ──────────────────────────────────────────────
def test_health_endpoint():
    """Test that /health returns 200."""
    from app.main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ──────────────────────────────────────────────
# Test 4: End-to-End (requires GEMINI_API_KEY)
# ──────────────────────────────────────────────
# Uncomment this test once you've completed ALL TODOs
# and have a valid API key in your .env file.

def test_review_code_endpoint():
    """End-to-end test of the /review-code endpoint."""
    from app.main import app

    client = TestClient(app)
    response = client.post("/review-code", json={
        "code": "def add(a, b): return a - b",
        "language": "python",
        "context": "Addition function"
    })
    assert response.status_code == 200
    data = response.json()
    assert "bugs" in data
    assert "summary" in data
    assert "score" in data
