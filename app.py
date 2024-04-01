from flask import Flask, abort, request, jsonify
from tempfile import NamedTemporaryFile
import whisper
import torch

torch.cuda.is_available()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

model = whisper.load_model("base", device=DEVICE)

app = Flask(__name__)

@app.route("/")
def hello():
    return "Whisper Here!"

@app.route('/whisper', methods=['POST'])
def handler():
    if 'file' not in request.files:
        abort(400, description="No files were provided.")

    results = []

    for filename, file in request.files.items():
        with NamedTemporaryFile(delete=True) as temp:
            file.save(temp.name)
            try:
                result = model.transcribe(temp.name)
                results.append({
                    'filename': filename,
                    'transcript': result['text'],
                })
            except Exception as e:
                abort(500, description=f"Error during transcription: {e}")

    return jsonify(results=results)
