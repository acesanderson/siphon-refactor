FROM pytorch/pytorch:2.9.0-cuda12.8-cudnn9-devel

# Install system dependencies
RUN apt-get update && apt-get install -y git

# Install Python deps
# IMPORTANT: Install diffusers from source to ensure Z-Image pipeline exists
RUN pip install --upgrade pip
RUN pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128 --upgrade
RUN pip install git+https://github.com/huggingface/diffusers.git
RUN pip install transformers accelerate protobuf sentencepiece fastapi uvicorn httpx pydantic

COPY . /app
WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
