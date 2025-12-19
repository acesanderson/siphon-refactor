# FILE: flux_sidecar/Dockerfile
FROM pytorch/pytorch:2.9.0-cuda12.8-cudnn9-devel

ENV DEBIAN_FRONTEND=noninteractive
# Force Python to log immediately (critical for seeing download progress)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Update Torch to Nightly (Specific for RTX 5090 / CUDA 12.8 support)
# We do this BEFORE requirements.txt to ensure the base torch version is correct
RUN pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128 --upgrade

# 2. Copy ONLY requirements.txt first
# This allows Docker to cache this layer. If you change main.py but not requirements,
# Docker will skip this slow install step on rebuilds.
COPY requirements.txt .

# 3. Install dependencies from file
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application code
COPY . .

# 5. Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
