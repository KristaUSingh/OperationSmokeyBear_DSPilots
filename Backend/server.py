# server.py
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from incident_parser.categorize import categorize_transcript
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

@app.get("/")
async def root():
    return {"status": "ok", "message": "Operation Smokey Bear backend is running!"}
