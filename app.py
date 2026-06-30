from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os
import shutil
import uuid
from google import genai
import os

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)
app = FastAPI()

import pathlib

import time

def analyze_video(video_path):

    uploaded = client.files.upload(file=video_path)

    while True:
        file_info = client.files.get(name=uploaded.name)

        state = str(file_info.state)

        print("File State:", state)

        if "ACTIVE" in state:
            break

        if "FAILED" in state:
            raise Exception("Gemini failed to process video.")

        time.sleep(5)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            file_info,
            """
Analyze this video.

Describe everything happening.

Then write a natural Burmese narration script.
"""
        ]
    )

    return response.text

# ==========================
# CORS (fix Failed to fetch)
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# Folders
# ==========================
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==========================
# Static files
# ==========================
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


# ==========================
# HOME PAGE
# ==========================
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Video Generator</title>

        <link rel="stylesheet" href="/static/css/style.css">
        <script defer src="/static/js/app.js"></script>
    </head>

    <body>

    <div class="container">

        <header>
            <h1>🎬 AI Video Generator</h1>
            <p>Upload video and generate AI result</p>
        </header>

        <div class="upload-card">

            <div class="upload-box">
                <input type="file" id="videoFile" accept="video/*">
            </div>

            <div class="options">

                <div class="option">
                    <label>Language</label>
                    <select id="language">
                        <option value="my">Myanmar</option>
                        <option value="en">English</option>
                    </select>
                </div>

                <div class="option">
                    <label>Voice</label>
                    <select id="voice">
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                    </select>
                </div>

                <div class="option">
                    <label>Ratio</label>
                    <select id="ratio">
                        <option value="9:16">9:16</option>
                        <option value="16:9">16:9</option>
                    </select>
                </div>

            </div>

            <button id="generateBtn">🚀 Upload & Generate</button>

            <video id="preview" controls></video>

        </div>

    </div>

    </body>
    </html>
    """


# ==========================
# UPLOAD API
# ==========================
@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    language: str = Form(...),
    voice: str = Form(...),
    ratio: str = Form(...)
):
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

  
script = analyze_video(file_path)

return JSONResponse({
    "status": "success",
    "message": "Upload completed",
    "filename": filename,
    "language": language,
    "voice": voice,
    "ratio": ratio,
    "script": script,
    "file_url": f"/uploads/{filename}"
})


# ==========================
# HEALTH CHECK
# ==========================
