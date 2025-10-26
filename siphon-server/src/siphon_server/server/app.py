from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from siphon_api.models import ProcessedContent
from siphon_server.core.pipeline import SiphonPipeline
from siphon_server.core.dependencies import get_pipeline

app = FastAPI(title="Siphon Server", version="2.0.0")


class ProcessRequest(BaseModel):
    source: str
    use_cache: bool = True
    model: str = "gpt-4o"


@app.post("/api/v2/process", response_model=ProcessedContent)
async def process_content(request: ProcessRequest) -> ProcessedContent:
    """Main endpoint - process any source"""
    try:
        pipeline = get_pipeline()
        result = pipeline.process(
            source=request.source,
            use_cache=request.use_cache,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log error
        raise HTTPException(status_code=500, detail="Processing failed")


@app.get("/api/v2/cache/{uri:path}", response_model=ProcessedContent)
async def get_cached(uri: str) -> ProcessedContent:
    """Retrieve from cache"""
    pipeline = get_pipeline()
    result = pipeline.cache.get(uri) if pipeline.cache else None
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
