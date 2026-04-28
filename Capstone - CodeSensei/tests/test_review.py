"""
CodeSensei — Tests
===================
Run these tests to verify your implementations.

Usage:
    pytest tests/ -v

═══════════════════════════════════════════════
  Tests are organized by Part:
    Part 1 tests: Schemas, Parser, Health, /review-code
    Part 2 tests: Extended schemas, Tools, Voice, /review-code-advanced
═══════════════════════════════════════════════
"""

import pytest
from fastapi.testclient import TestClient


# ╔═══════════════════════════════════════════════╗
# ║            PART 1 — Eval 2 Tests               ║
# ╚═══════════════════════════════════════════════╝


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
    from app.schemas import ReviewResponse, BugReport, Severity, Language

    bug = BugReport(
        bug_description="Test bug",
        severity=Severity.LOW,
        suggestion="Fix it"
    )
    response = ReviewResponse(
        bugs=[bug],
        summary="Found 1 bug",
        score=85,
        language=Language.PYTHON
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
# Uncomment this test once you've completed ALL Part 1 TODOs
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


# ╔═══════════════════════════════════════════════╗
# ║       PART 2 — Capstone Extension Tests        ║
# ╚═══════════════════════════════════════════════╝
# Uncomment these tests as you complete Part 2 TODOs.


# ──────────────────────────────────────────────
# Test 5: Part 2 Schema Validation
# ──────────────────────────────────────────────
def test_style_issue_creation():
    """Test that StyleIssue can be created."""
    from app.schemas import StyleIssue
    issue = StyleIssue(
        issue="Variable name 'x' is not descriptive",
        category="naming",
        suggestion="Use a descriptive name like 'count'",
        line_number=3
    )
    assert issue.category == "naming"
    assert issue.line_number == 3
def test_concept_explanation_creation():
    """Test that ConceptExplanation can be created."""
    from app.schemas import ConceptExplanation
    explanation = ConceptExplanation(
        concept="Off-by-one error",
        explanation="Occurs when a loop iterates one too many or few times",
        related_bug="Loop goes past array bounds",
        code_example="for i in range(len(arr)):"
    )
    assert explanation.concept == "Off-by-one error"
def test_coding_challenge_creation():
    """Test that CodingChallenge can be created."""
    from app.schemas import CodingChallenge
    challenge = CodingChallenge(
        title="Handle Empty Input",
        description="Modify the function to handle empty lists",
        difficulty="easy",
        starter_code="def find_max(numbers):\n    pass",
        hint="What should the function return for []?"
    )
    assert challenge.difficulty == "easy"
def test_full_review_response_creation():
    """Test that FullReviewResponse can be created."""
    from app.schemas import FullReviewResponse, Language
    response = FullReviewResponse(
        bugs=[],
        style_issues=[],
        explanations=[],
        challenges=[],
        summary="Great code!",
        score=95,
        language=Language.PYTHON,
        reasoning_trace="Thought: checking bugs..."
    )
    assert response.score == 95
    assert response.reasoning_trace is not None
def test_voice_review_request():
    """Test VoiceReviewRequest model."""
    from app.schemas import VoiceReviewRequest, Language
    req = VoiceReviewRequest(
        language=Language.PYTHON,
        context="Sorting function",
        use_advanced=True
    )
    assert req.use_advanced is True
# ──────────────────────────────────────────────
# Test 6: Voice Transcription
# ──────────────────────────────────────────────

def test_extract_code_from_transcript():
    """Test code extraction from a spoken transcript."""
    from app.voice import extract_code_from_transcript
    # Note: This test requires the LLM, so it needs an API key
    transcript = "define a function called add that takes a and b and returns a plus b"
    code, context = extract_code_from_transcript(transcript, "python")
    assert "def" in code
    assert "add" in code


# ──────────────────────────────────────────────
# Test 7: Advanced Review Endpoint (requires API key)
# ──────────────────────────────────────────────

def test_review_code_advanced_endpoint():
    """End-to-end test of the /review-code-advanced endpoint."""
    from app.main import app
    client = TestClient(app)
    response = client.post("/review-code-advanced", json={
        "code": "def add(a, b): return a - b",
        "language": "python",
        "context": "Addition function"
    })
    assert response.status_code == 200
    data = response.json()
    assert "bugs" in data
    assert "style_issues" in data
    assert "explanations" in data
    assert "challenges" in data
# ──────────────────────────────────────────────
# Test 8: Voice Review Endpoint (requires API key + audio)
# ──────────────────────────────────────────────

def test_review_voice_endpoint_invalid_file():
    """Test that /review-voice rejects non-audio files."""
    from app.main import app
    client = TestClient(app)
    # Send a text file instead of audio
    response = client.post(
        "/review-voice",
        files={"audio": ("test.txt", b"not audio", "text/plain")},
        data={"language": "python"}
    )
    assert response.status_code == 400
