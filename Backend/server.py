# server.py
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from incident_parser.categorize import categorize_transcript, categorize_audio_file
from incident_parser.providers import GeminiProvider

load_dotenv()  # optional: if you're using .env for GOOGLE_API_KEY

app = FastAPI()
# allow local frontend origins (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/categorize-transcript")
async def api_categorize_transcript(payload: dict):
    transcript = payload.get("transcript")
    if not transcript or not isinstance(transcript, str):
        raise HTTPException(status_code=400, detail="Provide 'transcript' (str).")

    try:
        provider = GeminiProvider()
        # Do not require fields from user — use categorize_transcript default
        result = categorize_transcript(transcript, provider=provider)

        # DEBUG START - PRINT JSON OUTPUT IN CONSOLE
        print("=== CATEGORIZATION RESULT ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("=== END RESULT ===")
        # DEBUG END
        return {"fields": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/categorize-audio")
async def api_categorize_audio(audio: UploadFile = File(...), fields: str = Form(...)):
    """
    fields can be a JSON array string or comma-separated list in 'fields' form field.
    """
    try:
        # parse fields
        try:
            parsed = json.loads(fields)
            if isinstance(parsed, list):
                fields_list = parsed
            else:
                raise ValueError
        except Exception:
            # fallback: comma separated
            fields_list = [f.strip() for f in fields.split(",") if f.strip()]

        # save uploaded file temporarily
        tmp_path = f"/tmp/{audio.filename}"
        with open(tmp_path, "wb") as f:
            f.write(await audio.read())

        provider = GeminiProvider()
        result = categorize_audio_file(tmp_path, fields_list, provider=provider)
        return {"fields": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "ok", "message": "Operation Smokey Bear backend is running!"}
