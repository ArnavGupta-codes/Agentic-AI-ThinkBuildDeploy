"""
CodeSensei — FastAPI Application
=================================
The web server that exposes our AI Code Review system
as a REST API endpoint.

Concepts used:
- FastAPI framework (Lecture 8)
- Pydantic request/response validation
- HTTP methods (POST, GET)
- Error handling with HTTPException

YOUR TASKS:
  TODO 1: Implement the POST /review-code endpoint
"""

from fastapi import FastAPI, HTTPException
from app.schemas import CodeReviewRequest, ReviewResponse

# ──────────────────────────────────────────────
# FastAPI App Instance (PROVIDED)
# ──────────────────────────────────────────────
app = FastAPI(
    title="CodeSensei",
    description="AI-Powered Code Review & Learning Platform",
    version="1.0.0",
)


# ──────────────────────────────────────────────
# Health Check Endpoint (PROVIDED)
# ──────────────────────────────────────────────
@app.get("/health")
def health_check():
    """Simple health check — verify the server is running."""
    return {
        "status": "healthy",
        "service": "CodeSensei",
        "version": "1.0.0"
    }


# ──────────────────────────────────────────────
# TODO 1: Code Review Endpoint
# ──────────────────────────────────────────────
# Create a POST endpoint at "/review-code" that:
#
#   1. Accepts a CodeReviewRequest as the request body
#      → FastAPI automatically validates it using Pydantic!
#
#   2. Calls run_coordinator() with the request data:
#      - code = request.code
#      - language = request.language.value (converts enum to string)
#      - context = request.context (may be None — handle it!)
#
#   3. Returns the ReviewResponse
#      → FastAPI automatically serializes it to JSON!
#
#   4. Wraps everything in try/except:
#      - On success: return the ReviewResponse
#      - On error: raise HTTPException(status_code=500, detail=str(e))
#
# Hints:
#   - Import run_coordinator from app.agents
#   - Use the @app.post() decorator with response_model=ReviewResponse
#   - The function can be sync (def) or async (async def) — either works
#
# Example request body (JSON):
#   {
#       "code": "def add(a, b): return a - b",
#       "language": "python",
#       "context": "Simple addition function"
#   }
#
# Example response (JSON):
#   {
#       "bugs": [
#           {
#               "bug_description": "Uses subtraction instead of addition",
#               "severity": "high",
#               "suggestion": "Change '-' to '+'",
#               "line_number": 1
#           }
#       ],
#       "summary": "Found 1 high-severity bug...",
#       "score": 60,
#       "language": "python"
#   }

# TODO: Write your endpoint here
# @app.post("/review-code", response_model=ReviewResponse)
# def review_code(request: CodeReviewRequest):
#     ...
from app.agents import run_coordinator
@app.post("/review-code", response_model=ReviewResponse)
def review_code(request: CodeReviewRequest):
    try:
        result = run_coordinator(
            code=request.code,
            language=request.language.value,
            context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))