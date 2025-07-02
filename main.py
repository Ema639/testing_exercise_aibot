import os
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

DEEP_AI_API_KEY = os.getenv("DEEP_AI_API_KEY")
DEEP_AI_URL = "https://api.deepai.org/api/nsfw-detector"

app = FastAPI()


@app.post("/moderate")
async def moderate_image(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    contents = await file.read()

    response = requests.post(
        DEEP_AI_URL,
        files={'image': contents},
        headers={'api-key': DEEP_AI_API_KEY},
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error from DeepAI API")

    result = response.json()

    nsfw_score = result.get("output", {}).get("nsfw_score")

    if nsfw_score is None:
        raise HTTPException(status_code=500, detail="Invalid response from DeepAI")

    if nsfw_score > 0.7:
        return JSONResponse(content={"status": "REJECTED", "reason": "NSFW content"})
    else:
        return {"status": "OK"}
