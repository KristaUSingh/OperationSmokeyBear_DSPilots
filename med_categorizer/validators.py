from typing import Dict, List

def force_string_dict(obj, fields: List[str]) -> Dict[str, str]:
    """
    Coerce any model output into {field: str}. Missing -> "", non-strings -> str().
    Extra keys are dropped; missing keys are added as "".
    """
    out = {}
    if isinstance(obj, dict):
        for f in fields:
            v = obj.get(f, "")
            if v is None:
                v = ""
            elif not isinstance(v, str):
                v = str(v)
            out[f] = v.strip()
    else:
        # Completely malformed → empty dict with expected keys
        out = {f: "" for f in fields}
    return out