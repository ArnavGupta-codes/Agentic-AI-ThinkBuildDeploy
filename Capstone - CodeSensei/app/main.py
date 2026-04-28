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
- File uploads (Part 2)

═══════════════════════════════════════════════
  PART 1 (Eval 2) — YOUR TASKS:
    TODO 1: Implement the POST /review-code endpoint

  PART 2 (Capstone Extension) — YOUR TASKS:
    TODO 2: Implement the POST /review-code-advanced endpoint
    TODO 3: Implement the POST /review-voice endpoint
═══════════════════════════════════════════════
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from app.schemas import CodeReviewRequest, ReviewResponse, FullReviewResponse, VoiceReviewRequest
from app.agents import run_react_coordinator, run_coordinator
from app.voice import transcribe_audio, extract_code_from_transcript

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


# ╔═══════════════════════════════════════════════╗
# ║            PART 1 — Eval 2 TODOs              ║
# ╚═══════════════════════════════════════════════╝


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

# ← Your POST /review-code endpoint here
from app.agents import run_coordinator

@app.post("/review-code", response_model=ReviewResponse)
def review_code(request: CodeReviewRequest):
    try:
        review = run_coordinator(
            code=request.code,
            language=request.language.value,
            context=str(request.context)
        )
        return review
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ╔═══════════════════════════════════════════════╗
# ║       PART 2 — Capstone Extension TODOs        ║
# ╚═══════════════════════════════════════════════╝
# Complete these AFTER finishing Part 1.
#
# NOTE: You'll need to import additional functions and schemas.
# Uncomment the imports below once you've implemented them:
#

# ──────────────────────────────────────────────
# TODO 2: Advanced Code Review Endpoint
# ──────────────────────────────────────────────
# Create a POST endpoint at "/review-code-advanced" that
# uses the ReAct coordinator with ALL agents (Bug Detector,
# Style & Quality, Concept Explainer, Challenge Generator).
#
# This endpoint works the same as /review-code but uses
# the full multi-agent pipeline for a comprehensive review.
#
#   1. Accepts a CodeReviewRequest as the request body
#      (same input as /review-code)
#
#   2. Calls run_react_coordinator() with the request data:
#      - code = request.code
#      - language = request.language.value
#      - context = request.context or ""
#
#   3. Returns a FullReviewResponse (the extended response
#      with bugs, style issues, explanations, and challenges)
#
#   4. Wraps in try/except with HTTPException on error
#
# Example response (JSON):
#   {
#       "bugs": [...],
#       "style_issues": [...],
#       "explanations": [...],
#       "challenges": [...],
#       "summary": "Comprehensive review...",
#       "score": 72,
#       "language": "python",
#       "reasoning_trace": "Thought: I should first..."
#   }

@app.post("/review-code-advanced", response_model=FullReviewResponse)
def review_code_advanced(request: CodeReviewRequest):
    try:
        review = run_react_coordinator(
            code=request.code,
            language=request.language.value,
            context=request.context or ""
        )
        return review
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────
# TODO 3: Voice-to-Code Review Endpoint
# ──────────────────────────────────────────────
# Create a POST endpoint at "/review-voice" that accepts
# an audio file, transcribes it to text, extracts the code,
# and then runs a code review on it.
#
# This is a multi-step pipeline:
#   Audio → Transcribe → Extract Code → Review Code
#
# Implementation steps:
#
#   1. Define the endpoint with file upload support:
#      @app.post("/review-voice")
#      async def review_voice(
#          audio: UploadFile = File(...),
#          language: str = Form(...),
#          context: str = Form(None),
#          use_advanced: bool = Form(False),
#      ):
#
#      Note: We use Form() instead of JSON body because
#      file uploads require multipart/form-data encoding.
#
#   2. Read the audio file content:
#      audio_bytes = await audio.read()
#
#   3. Validate the file:
#      - Check that it's an audio file (check audio.content_type)
#      - Supported types: "audio/wav", "audio/mp3", "audio/mpeg",
#        "audio/ogg", "audio/webm"
#      - Raise HTTPException(400) if invalid
#
#   4. Transcribe the audio to text:
#      transcript = transcribe_audio(audio_bytes, audio.content_type)
#
#   5. Extract code from the transcript:
#      code, extracted_context = extract_code_from_transcript(
#          transcript, language
#      )
#
#   6. Combine contexts:
#      full_context = context or ""
#      if extracted_context and extracted_context != "none":
#          full_context += f" {extracted_context}"
#
#   7. Run the appropriate review:
#      - If use_advanced is True → run_react_coordinator()
#      - If use_advanced is False → run_coordinator()
#
#   8. Return the response with the transcript included:
#      Return a dict with the review response fields PLUS:
#      - "transcript": the raw transcript text
#      - "extracted_code": the code extracted from speech
#
#   9. Wrap in try/except with HTTPException on error
#
# Example curl command:
#   curl -X POST http://localhost:8000/review-voice \
#     -F "audio=@my_code.wav" \
#     -F "language=python" \
#     -F "context=Sorting function" \
#     -F "use_advanced=false"

# ← Your POST /review-voice endpoint here
@app.post("/review-voice")
async def review_voice(
    audio: UploadFile = File(...),
    language: str = Form(...),
    context: str = Form(None),
    use_advanced: bool = Form(False),
):
    try:
        # Validate audio file type
        supported_types = {"audio/wav", "audio/mp3", "audio/mpeg", "audio/ogg", "audio/webm"}
        if audio.content_type not in supported_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio type. Supported: {', '.join(supported_types)}"
            )
        
        # Read audio file
        audio_bytes = await audio.read()
        
        # Transcribe audio
        transcript = transcribe_audio(audio_bytes, audio.content_type)
        
        # Extract code from transcript
        code, extracted_context = extract_code_from_transcript(transcript, language)
        
        # Combine contexts
        full_context = context or ""
        if extracted_context and extracted_context.lower() != "none":
            full_context += f" {extracted_context}"
        
        # Run the appropriate review
        if use_advanced:
            review = run_react_coordinator(code=code, language=language, context=full_context)
        else:
            review = run_coordinator(code=code, language=language, context=full_context)
        
        # Return response with transcript and extracted code
        response = review.dict() if hasattr(review, 'dict') else dict(review)
        response["transcript"] = transcript
        response["extracted_code"] = code
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))