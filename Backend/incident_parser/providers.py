# providers.py
import os, json
from typing import Dict, List, Optional
from .prompt import build_extraction_prompt, field_descriptions

# ---- Provider interface ----
class LLMProvider:
    def extract_fields(self, transcript: str, fields: List[str]) -> Dict[str, str]:
        raise NotImplementedError

class GeminiProvider(LLMProvider):
    """
    Google Gemini provider for strict JSON field extraction.
    Uses response_mime_type='application/json' to coerce JSON output.
    """
    def __init__(
        self,
        model_name: str = "gemini-2.5-flash-lite", 
        temperature: float = 0.0,
        max_output_tokens: int = 1024,
        safety_settings: Optional[list] = None,
    ):
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("Set GOOGLE_API_KEY for GeminiProvider.")
        genai.configure(api_key=api_key)

        # Put the system prompt where Gemini expects it
        from .prompt import SYSTEM_INSTRUCTIONS
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_INSTRUCTIONS,
        )
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.safety_settings = safety_settings  # can be None to use defaults

    def extract_fields(self, transcript: str, fields: List[str]) -> Dict[str, dict]:
        """
        Extracts fields using Gemini and returns both value and confidence per field.
        Example output:
        {
        "incident_type": {"value": "Fire", "confidence": 0.92},
        "incident_location": {"value": "Los Angeles", "confidence": 0.88}
        }
        """
        prompt = build_extraction_prompt(transcript, fields, field_descriptions=None)
        user = prompt + "\nReturn ONLY compact JSON."

        gen_config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "response_mime_type": "application/json",
        }

        try:
            resp = self.model.generate_content(
                contents=[{"role": "user", "parts": [{"text": user}]}],
                generation_config=gen_config,
                safety_settings=self.safety_settings,
            )

            # Extract response text safely
            text = (getattr(resp, "text", "") or "").strip()
            if not text:
                # Attempt fallback extraction from candidates
                candidates = getattr(resp, "candidates", []) or []
                if candidates and candidates[0].content and candidates[0].content.parts:
                    pieces = [
                        p.text for p in candidates[0].content.parts if hasattr(p, "text") and p.text
                    ]
                    text = "\n".join(pieces).strip()

        except Exception:
            # If Gemini call fails, return empty defaults
            return {f: {"value": "", "confidence": 0.0} for f in fields}

        # Try parsing JSON safely
        data = self._safe_json(text)
        results = {}

        for f in fields:
            entry = data.get(f, {})
            if isinstance(entry, dict):
                results[f] = {
                    "value": str(entry.get("value", "")).strip(),
                    "confidence": float(entry.get("confidence", 0.0)),
                }
            else:
                results[f] = {"value": str(entry).strip(), "confidence": 0.0}

        return results
    
    @staticmethod
    def _safe_json(text: str):
        """Attempts to parse JSON safely, even if Gemini adds formatting."""
        import json
        t = (text or "").strip()

        # Try direct parse
        try:
            return json.loads(t)
        except Exception:
            pass

        # Try stripping Markdown fences
        if t.startswith("```"):
            t2 = t.strip("`")
            if t2.lower().startswith("json"):
                t2 = t2[4:].strip()
            try:
                return json.loads(t2)
            except Exception:
                pass

        # Try substring between first and last braces
        start, end = t.find("{"), t.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(t[start:end+1])
            except Exception:
                pass

        # If nothing works, return empty dict
        return {}

