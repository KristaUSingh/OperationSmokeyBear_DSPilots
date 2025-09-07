#categorize.py
from typing import Dict, List, Optional
from .transcribe import transcribe_audio
from .providers import LLMProvider, GeminiProvider
import os
from dotenv import load_dotenv
load_dotenv()

def _default_provider() -> LLMProvider:
    kind = (os.getenv("LLM_PROVIDER") or "gemini").lower()
    if kind == "gemini":
        return GeminiProvider()
    else:
        raise ValueError(f"Unknown provider: {kind}")

def categorize_audio_file(
    audio_path: str,
    fields: List[str],
    transcribe_model: str = "base",
    provider: Optional[LLMProvider] = None,
) -> Dict[str, str]:
    if not fields:
        raise ValueError("Must provide at least one field name to extract.")
    transcript = transcribe_audio(audio_path, model_name=transcribe_model)
    if provider is None:
        provider = _default_provider()
    return provider.extract_fields(transcript, fields)


def categorize_transcript(
    transcript: str,
    fields: List[str],
    provider: Optional[LLMProvider] = None,
) -> Dict[str, str]:
    if not fields:
        raise ValueError("Must provide at least one field name to extract.")
    if provider is None:
        provider = _default_provider()
    return provider.extract_fields(transcript, fields)