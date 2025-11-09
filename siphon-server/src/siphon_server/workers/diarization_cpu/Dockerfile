FROM python:3.10-slim
WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN uv pip install --system 'numpy<2'
RUN uv pip install --system 'torch==2.1.2' 'torchaudio==2.1.2' --index-url https://download.pytorch.org/whl/cpu
RUN uv pip install --system 'huggingface-hub<0.20.0'
RUN uv pip install --system 'pyannote.audio==3.1.1' soundfile fastapi "uvicorn[standard]" python-multipart

COPY diarize.py .
COPY main.py .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
