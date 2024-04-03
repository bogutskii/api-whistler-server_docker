from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse
from tempfile import NamedTemporaryFile
import whisper
import torch
from typing import List
import asyncio

torch.cuda.is_available()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

app = FastAPI()
model = None


async def load_model():
    global model
    model = whisper.load_model("base", device=DEVICE)


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, load_model)


@app.post("/whisper/")
async def handler(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files were provided")

    results = []

    for file in files:
        with NamedTemporaryFile(delete=True) as temp:
            content = await file.read()
            with open(temp.name, "wb") as temp_file:
                temp_file.write(content)

            result = model.transcribe(temp.name)

            results.append({
                'filename': file.filename,
                'transcript': result['text'],
            })

    return JSONResponse(content={'results': results})


@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url='/docs')


@app.get("/change_model/")
def change_model(model_name: str = Query(default="base", enum=["base", "small", "medium", "large"])):
    try:
        load_model(model_name)
        return {"message": f"Model changed to {model_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
