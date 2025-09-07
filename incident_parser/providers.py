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

    def extract_fields(self, transcript: str, fields: List[str]) -> Dict[str, str]:
        from .validators import force_string_dict
        prompt = build_extraction_prompt(transcript, fields, field_descriptions=None)
        user = prompt + "\nReturn ONLY compact JSON."

        gen_config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "response_mime_type": "application/json",  # request JSON
        }

        try:
            resp = self.model.generate_content(
                contents=[{"role": "user", "parts": [{"text": user}]}],
                generation_config=gen_config,
                safety_settings=self.safety_settings,
            )
            # resp.text can be None if blocked or empty
            text = (getattr(resp, "text", "") or "").strip()
            if not text:
                # Attempt to stitch from candidates if needed
                candidates = getattr(resp, "candidates", []) or []
                if candidates and candidates[0].content and candidates[0].content.parts:
                    # Join any text parts we can see
                    pieces = []
                    for p in candidates[0].content.parts:
                        if hasattr(p, "text") and p.text:
                            pieces.append(p.text)
                    text = "\n".join(pieces).strip()
        except Exception:
            return {f: "" for f in fields}

        data = self._safe_json(text)
        return force_string_dict(data, fields)

    @staticmethod
    def _safe_json(text: str):
        import json
        t = (text or "").strip()
        # 1) direct parse
        try:
            return json.loads(t)
        except Exception:
            pass
        # 2) strip code fences
        if t.startswith("```"):
            t2 = t.strip("`")
            if t2.lower().startswith("json"):
                t2 = t2[4:].strip()
            try:
                import json as _json
                return _json.loads(t2)
            except Exception:
                pass
        # 3) brace-bounded substring
        start, end = t.find("{"), t.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(t[start:end+1])
            except Exception:
                pass
        return {}