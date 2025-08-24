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

# Paths to JSON files
JSON_FILE_PATH = "patients.json"
JSON_FILE_PATH_2 = "patients_copy.json"

# Keep track of which file to serve
toggle = {"use_first": True}


@app.get("/patients")
async def get_patients():
    # Decide which file to use
    file_path = JSON_FILE_PATH if toggle["use_first"] else JSON_FILE_PATH_2
    toggle["use_first"] = not toggle["use_first"]  # Flip toggle for next request

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"JSON file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON format in {file_path}")
