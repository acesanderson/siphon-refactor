import asyncio
import torch
import io
import os
import logging
from fastapi import FastAPI, Response, HTTPException
from fastapi.concurrency import run_in_threadpool
from contextlib import asynccontextmanager
from pydantic import BaseModel

# Z-Image requires the latest diffusers
from diffusers import ZImagePipeline

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("zimage_loader")

# Global state
pipe = None
gpu_lock = asyncio.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipe
    # Z-Image-Turbo is the 8-step distilled version
    model_id = "Tongyi-MAI/Z-Image-Turbo"

    try:
        logger.info(f"--- STEP 1: LOADING PIPELINE FOR {model_id} ---")

        # Load directly in bfloat16 (RTX 5090 handles this easily)
        # We generally don't need snapshot_download explicit calls with diffusers
        # unless you want to manage cache paths manually, from_pretrained handles it.
        pipe = ZImagePipeline.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=False,  # We have 32GB VRAM, load it fast
        )

        # Move to GPU
        pipe.to("cuda")

        # Optional: Flash Attention (5090 supports this natively and it's fast)
        try:
            pipe.transformer.set_attention_backend("flash")
            logger.info("Flash Attention enabled.")
        except Exception as e:
            logger.warning(f"Could not enable Flash Attention: {e}")

        # Optional: Compile (might increase startup time but speeds up inference)
        # pipe.transformer.compile()

        logger.info("--- READY: Z-IMAGE MODEL LOADED ---")

    except Exception as e:
        logger.error(f"CRITICAL FAILURE: {e}")
        raise e

    yield
    logger.info("Shutting down...")
    if pipe:
        del pipe
        torch.cuda.empty_cache()


app = FastAPI(lifespan=lifespan)


class GenRequest(BaseModel):
    prompt: str
    height: int = 1024
    width: int = 1024
    # Turbo optimized for 8 steps (input 9 usually results in 8 forwards)
    steps: int = 9
    # Turbo requires guidance_scale 0.0
    guidance: float = 0.0
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

    async with gpu_lock:

        def _inference():
            generator = torch.Generator("cuda").manual_seed(req.seed)

            # Z-Image specific call parameters
            image = pipe(
                prompt=req.prompt,
                height=req.height,
                width=req.width,
                num_inference_steps=req.steps,
                guidance_scale=req.guidance,
                generator=generator,
            ).images[0]

            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="PNG")
            return img_byte_arr.getvalue()

        img_bytes = await run_in_threadpool(_inference)

    return Response(content=img_bytes, media_type="image/png")
