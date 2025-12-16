# FILE: flux_sidecar/main.py
import asyncio
import torch
import io
import os
from fastapi import FastAPI, Response, HTTPException
from fastapi.concurrency import run_in_threadpool
from contextlib import asynccontextmanager
from diffusers import Flux2Pipeline
from pydantic import BaseModel

# Global state
pipe = None
gpu_lock = asyncio.Lock()  # Prevent simultaneous GPU access


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipe
    print("Initializing FLUX.2-dev sidecar...")

    # Check for Hugging Face Token
    if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
        print("WARNING: HUGGINGFACEHUB_API_TOKEN is not set. Model download may fail.")

    try:
        print("Loading model weights... (This happens once)")
        # FLUX.2-dev is the specific model you asked for
        pipe = Flux2Pipeline.from_pretrained(
            "black-forest-labs/FLUX.2-dev", torch_dtype=torch.bfloat16
        )
        # Move to GPU. 32GB VRAM on 5090 is massive, so we can keep it fully loaded.
        pipe.to("cuda")
        print("FLUX.2-dev loaded and ready on RTX 5090.")
    except Exception as e:
        print(f"CRITICAL ERROR loading model: {e}")
        # We don't raise here so the container stays alive for debugging,
        # but health checks will fail.
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)


class GenRequest(BaseModel):
    prompt: str
    height: int = 1024
    width: int = 1024
    steps: int = 40  # Flux usually looks good around 30-50
    guidance: float = 3.5
    seed: int = 42


@app.get("/health")
async def health_check():
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model loading or failed")
    return {"status": "healthy", "gpu": torch.cuda.get_device_name(0)}


@app.post("/generate")
async def generate_image(req: GenRequest):
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not initialized")

    # Use lock to ensure single-threaded GPU access
    async with gpu_lock:

        def _inference():
            generator = torch.Generator("cuda").manual_seed(req.seed)
            image = pipe(
                req.prompt,
                height=req.height,
                width=req.width,
                num_inference_steps=req.steps,
                guidance_scale=req.guidance,
                generator=generator,
            ).images[0]

            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="PNG")
            return img_byte_arr.getvalue()

        # Run blocking torch code in threadpool
        img_bytes = await run_in_threadpool(_inference)

    return Response(content=img_bytes, media_type="image/png")
