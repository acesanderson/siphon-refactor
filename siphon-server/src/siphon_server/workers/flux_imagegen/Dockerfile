# FILE: flux_sidecar/Dockerfile
# PERPLEXITY REC: Official PyTorch image with CUDA 12.8 + cuDNN 9 + Python pre-packaged.
# This matches the RTX 5090 (sm_120) requirements perfectly.
FROM pytorch/pytorch:2.9.0-cuda12.8-cudnn9-devel

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# The base image already has a pytorch install, but we need to ensure 
# it's the specific nightly build if the base one lags behind.
# The Perplexity note suggests we might still need to pip install the exact wheel
# just to be safe, though the base image might already have it.
# We will run this just in case to pin the version.
RUN pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128 --upgrade

# Install Flux.2 / Diffusers dependencies
# Note: 'sentencepiece' and 'protobuf' are critical for the Flux tokenizer
RUN pip install --no-cache-dir \
    transformers \
    accelerate \
    safetensors \
    diffusers \
    sentencepiece \
    protobuf \
    fastapi \
    uvicorn \
    python-multipart \
    httpx \
    bitsandbytes 
    # ^ bitsandbytes might fail if not compiled for cu128 yet. 
    # If it fails, remove it; you have 32GB VRAM so you might not need 4-bit quantization.

# Copy application code
COPY . .

# Command to run the service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
