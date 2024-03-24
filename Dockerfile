FROM python:3.10-slim

WORKDIR /python-docker

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends git ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install -r requirements.txt \
    && pip3 install "git+https://github.com/openai/whisper.git#egg=whisper&subdirectory=whisper" \
    && rm -rf /root/.cache/pip/*

COPY . .

CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "$PORT"]