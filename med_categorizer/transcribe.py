import os
from typing import Optional
import whisper

# Local Whisper (no API). If you prefer OpenAI/Deepgram/etc.,
# swap this with their SDK while keeping the same function signature.

_WHISPER_MODEL = None

def _get_model(model_name: str = "base"):
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        _WHISPER_MODEL = whisper.load_model(model_name)
    return _WHISPER_MODEL

def transcribe_audio(file_path: str, model_name: str = "base") -> str:
    """
    Returns a raw transcript string from an audio file.
    """
    model = _get_model(model_name)
    result = model.transcribe(file_path)
    return result.get("text", "").strip()