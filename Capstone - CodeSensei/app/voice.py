"""
CodeSensei — Voice-to-Text Module
===================================
Handles audio transcription and code extraction from
spoken descriptions. Students can speak their code aloud
and have it reviewed!

Concepts used:
- Google Gemini multimodal API (audio → text)
- LangChain for transcript parsing
- File handling and audio processing

═══════════════════════════════════════════════
  PART 2 (Capstone Extension) — YOUR TASKS:
    TODO 1: Implement the transcribe_audio() function
    TODO 2: Implement the extract_code_from_transcript() function
═══════════════════════════════════════════════

How Voice-to-Text works in CodeSensei:
    1. Student uploads an audio file (wav, mp3, ogg, webm)
    2. transcribe_audio() sends it to Gemini's multimodal API
    3. Gemini returns a text transcription
    4. extract_code_from_transcript() uses an LLM to parse
       the transcription and extract actual code
    5. The extracted code is then sent through the normal
       review pipeline

Example flow:
    Student says: "Define a function called add that takes
    a and b as parameters and returns a minus b"

    Transcription: "Define a function called add that takes
    a and b as parameters and returns a minus b"

    Extracted code: "def add(a, b):\\n    return a - b"
"""

import base64
from typing import Tuple

from app.config import llm, GEMINI_API_KEY
from app.prompts import TRANSCRIPT_PARSER_PROMPT
import google.generativeai as genai  # type: ignore
genai.configure(api_key=GEMINI_API_KEY)  # type: ignore
model = genai.GenerativeModel("gemini-2.5-flash")  # type: ignore


# ──────────────────────────────────────────────
# TODO 1: Implement the transcribe_audio() function
# ──────────────────────────────────────────────
# This function takes raw audio bytes and returns a
# text transcription using Google Gemini's multimodal API.
#
# Function signature:
#   def transcribe_audio(
#       audio_bytes: bytes,
#       content_type: str = "audio/wav"
#   ) -> str:
#
# Steps:
#   1. Import the Google Generative AI library:
#      import google.generativeai as genai
#
#   2. Configure the API:
#      genai.configure(api_key=GEMINI_API_KEY)
#
#   3. Create a Gemini model instance (use gemini-2.5-flash
#      which supports multimodal input):
#      model = genai.GenerativeModel("gemini-2.5-flash")
#
#   4. Prepare the audio data for the API:
#      - Encode the audio bytes to base64:
#        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
#      - Create the content parts:
#        audio_part = {
#            "inline_data": {
#                "mime_type": content_type,
#                "data": audio_b64
#            }
#        }
#
#   5. Send to Gemini with a transcription prompt:
#      response = model.generate_content([
#          "Please transcribe the following audio exactly. "
#          "The speaker is describing or dictating code. "
#          "Transcribe everything they say word for word.",
#          audio_part
#      ])
#
#   6. Return the transcription text:
#      return response.text
#
#   7. Handle errors:
#      - If the API call fails, raise a ValueError with
#        a helpful message
#      - If the response is empty, return a default message
#
# Example:
#   transcript = transcribe_audio(audio_bytes, "audio/wav")
#   # Returns: "define a function called add that takes a and b..."

def transcribe_audio(audio_bytes: bytes, content_type: str = "audio/wav") -> str:
    """
    Transcribe audio to text using Gemini's multimodal API.

    Args:
        audio_bytes: Raw audio file content
        content_type: MIME type (e.g., "audio/wav", "audio/mp3")

    Returns:
        Transcribed text string
    """
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    audio_part = {
            "inline_data": {
                "mime_type": content_type,
                "data": audio_b64
            }
        }
    response = model.generate_content([
          "Please transcribe the following audio exactly. "
          "The speaker is describing or dictating code. "
          "Transcribe everything they say word for word.",
          audio_part
      ])
    return response.text



# ──────────────────────────────────────────────
# TODO 2: Implement extract_code_from_transcript()
# ──────────────────────────────────────────────
# This function takes a raw transcript of someone speaking
# their code and extracts actual, formatted code from it.
#
# Function signature:
#   def extract_code_from_transcript(
#       transcript: str,
#       language: str
#   ) -> Tuple[str, str]:
#
# Steps:
#   1. Create the chain using your TRANSCRIPT_PARSER_PROMPT:
#      chain = TRANSCRIPT_PARSER_PROMPT | llm
#
#   2. Invoke with the transcript and language:
#      result = chain.invoke({
#          "transcript": transcript,
#          "language": language,
#      })
#
#   3. Parse the LLM output to extract:
#      - CODE: <the formatted code>
#      - CONTEXT: <any context the student mentioned>
#      (similar parsing to how you parse bug reports)
#
#   4. Return a tuple: (code, context)
#      - code: The extracted, properly formatted code
#      - context: Any additional context (or empty string)
#
#   5. Handle errors:
#      - If parsing fails, return (transcript, "")
#        as a fallback (treat the raw transcript as code)
#
# Example:
#   transcript = "define a function add with parameters a and b
#                  that returns a minus b"
#   code, ctx = extract_code_from_transcript(transcript, "python")
#   # code = "def add(a, b):\n    return a - b"
#   # ctx = ""
#
# Why is this needed?
#   When students speak their code, they use natural language.
#   "open paren" → (, "colon" → :, "indent" → whitespace
#   The TRANSCRIPT_PARSER_PROMPT helps the LLM convert
#   spoken descriptions into actual code.

def extract_code_from_transcript(transcript: str, language: str) -> Tuple[str, str]:
    """
    Extract code and context from a voice transcript.

    Args:
        transcript: Raw text transcription of spoken code
        language: Programming language

    Returns:
        Tuple of (extracted_code, extracted_context)
    """
    chain = TRANSCRIPT_PARSER_PROMPT | llm
    try:
        result = chain.invoke({
            "transcript": transcript,
            "language": language,
        })
        # Parse the result to extract CODE and CONTEXT
        raw_output = str(result.content)
        code = ""
        context = ""
        for line in raw_output.splitlines():
            if line.startswith("CODE:"):
                code = line.split("CODE:")[1].strip()
            elif line.startswith("CONTEXT:"):
                context = line.split("CONTEXT:")[1].strip()
        return code if code else transcript, context
    except Exception as e:
        # If parsing fails, return the raw transcript as code
        return transcript, ""   
        
