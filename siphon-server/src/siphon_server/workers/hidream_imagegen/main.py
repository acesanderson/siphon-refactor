import asyncio
import torch
import io
import os
import logging
from fastapi import FastAPI, Response, HTTPException
from fastapi.concurrency import run_in_threadpool
from contextlib import asynccontextmanager
from pydantic import BaseModel
from diffusers import HiDreamImagePipeline, HiDreamImageTransformer2DModel
from transformers import LlamaForCausalLM, AutoTokenizer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hidream_loader")

pipe = None
gpu_lock = asyncio.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipe
    model_id = "HiDream-ai/HiDream-I1-Dev"

    try:
        logger.info(f"--- LOADING HIDREAM COMPONENTS MANUALLY ---")
        hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

        # Load the heavy transformer directly from its subfolder
        # This resolves the 'Error no file named model.safetensors' issue
        transformer = HiDreamImageTransformer2DModel.from_pretrained(
            model_id,
            subfolder="transformer",
            torch_dtype=torch.bfloat16,
            token=hf_token,
        )

        # Assemble the pipeline injecting the transformer
        pipe = HiDreamImagePipeline.from_pretrained(
            model_id,
            transformer=transformer,
            torch_dtype=torch.bfloat16,
            token=hf_token,
            use_safetensors=True,
        )

        pipe.to("cuda")

        # Enable the Flash Attention we just installed
        try:
            pipe.transformer.set_attention_backend("flash")
            logger.info("Flash Attention enabled successfully.")
        except Exception as e:
            logger.warning(f"Could not trigger Flash Attention: {e}")

        logger.info("--- READY: HIDREAM ASSEMBLED ---")

    except Exception as e:
        logger.error(f"CRITICAL FAILURE: {e}")
        raise e

    yield
    if pipe:
        del pipe
        torch.cuda.empty_cache()


app = FastAPI(lifespan=lifespan)


class GenRequest(BaseModel):
    prompt: str
    height: int = 1024
    width: int = 1024
    steps: int = 28
    guidance: float = 0.0  # Dev/Fast versions usually use 0.0
    seed: int = 42


@app.get("/health")
async def health_check():
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "gpu": torch.cuda.get_device_name(0)}


@app.post("/generate")
async def generate_image(req: GenRequest):
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not initialized")

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

        img_bytes = await run_in_threadpool(_inference)

    return Response(content=img_bytes, media_type="image/png")
