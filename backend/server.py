from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import json
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your Next.js URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to your JSON file
JSON_FILE_PATH = "patients.json"

@app.get("/patients")
async def get_patients():
    if not os.path.exists(JSON_FILE_PATH):
        raise HTTPException(status_code=404, detail="JSON file not found")

    try:
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON format in file")
