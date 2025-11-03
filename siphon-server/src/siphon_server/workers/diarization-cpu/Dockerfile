# 1. Start from the exact Python version we need
FROM python:3.10-slim

# 2. Set up our working directory
WORKDIR /app

# 3. Install system dependencies (like ffmpeg for audio)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# 4. Install Python dependencies
# THIS IS THE MOST IMPORTANT STEP
# We force-install the CPU-only version of torch.
RUN pip install torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu

# 5. Copy our pyproject.toml and install the *old* libraries
COPY pyproject.toml .
# Assuming pyproject.toml lists pyannote.audio==3.1.1, etc.
RUN pip install .

# 6. Copy our application code
COPY diarize.py .
COPY main.py .

# 7. Expose the port for the API server
EXPOSE 8000

# 8. Define the command to run the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
