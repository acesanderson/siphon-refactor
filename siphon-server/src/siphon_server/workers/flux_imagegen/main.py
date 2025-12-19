import asyncio
import torch
import io
import os
import logging
from fastapi import FastAPI, Response, HTTPException
from fastapi.concurrency import run_in_threadpool
from contextlib import asynccontextmanager
from huggingface_hub import snapshot_download
from pydantic import BaseModel

# --- UPDATED IMPORTS ---
from transformers import BitsAndBytesConfig
from diffusers import FluxPipeline, FluxTransformer2DModel
# -----------------------

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flux_loader")

# Global state
pipe = None
gpu_lock = asyncio.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipe

    # NOTE: Ensure this matches what you actually have access to.
    # Standard public model is "black-forest-labs/FLUX.1-dev"
    model_id = "black-forest-labs/FLUX.1-dev"

    try:
        logger.info(f"--- STEP 1: CHECKING/DOWNLOADING WEIGHTS FOR {model_id} ---")
        model_path = snapshot_download(
            repo_id=model_id,
            repo_type="model",
            token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        )
        logger.info(f"Download complete. Model cached at: {model_path}")

        logger.info("--- STEP 2: LOADING QUANTIZED TRANSFORMER ---")

        # 1. Define the 8-bit config
        quant_config = BitsAndBytesConfig(
            load_in_8bit=True,
            # optional: llm_int8_threshold=6.0
        )

        # 2. Load ONLY the heavy Transformer in 8-bit
        # This keeps the text encoders in high precision (bfloat16) for quality
        transformer = FluxTransformer2DModel.from_pretrained(
            model_path,
            subfolder="transformer",
            quantization_config=quant_config,
            torch_dtype=torch.bfloat16,
        )

        logger.info("--- STEP 3: ASSEMBLING PIPELINE ---")
        # 3. Load the rest of the pipeline, injecting the 8-bit transformer
        pipe = FluxPipeline.from_pretrained(
            model_path, transformer=transformer, torch_dtype=torch.bfloat16
        )

        # 4. Use CPU Offload (It works perfectly with 8-bit components)
        pipe.enable_model_cpu_offload()

        logger.info("--- READY: MODEL LOADED (8-BIT TRANSFORMER) ---")

    except Exception as e:
        logger.error(f"CRITICAL FAILURE: {e}")

    yield
    logger.info("Shutting down...")


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

        # Run blocking torch code in threadpool
        img_bytes = await run_in_threadpool(_inference)

    return Response(content=img_bytes, media_type="image/png")
