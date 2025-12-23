# Exact base image used in your zimage worker
FROM pytorch/pytorch:2.9.0-cuda12.8-cudnn9-devel

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
# Limit parallel jobs during build to prevent VRAM/RAM exhaustion on your 5090
ENV MAX_JOBS=4 

# 1. Install system dependencies for protobuf and tokenizer conversion
RUN apt-get update && apt-get install -y \
    git \
    protobuf-compiler \
    libprotobuf-dev \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 2. Install core ML stack
# We include protobuf and specific versions of transformers/diffusers for HiDream support
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    httpx \
    python-multipart \
    pydantic \
    transformers>=4.48.0 \
    diffusers>=0.32.1 \
    accelerate \
    sentencepiece \
    protobuf \
    bitsandbytes \
    huggingface_hub

# 3. Install Flash Attention 2
# We use --no-build-isolation to ensure it uses the PyTorch versions already in the image
RUN pip install flash-attn --no-build-isolation

WORKDIR /app
COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
