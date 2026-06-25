"""FastAPI entrypoint for the DevOps Docs RAG Assistant."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.config import settings
from app.rag.pipeline import RagPipeline

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("devops-rag")

app = FastAPI(title="DevOps Docs RAG Assistant", version="0.1.0")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Lazily-loaded pipeline so the process can start (and /health can respond)
# even if the index or API keys are missing — useful during deploy/health checks.
_pipeline: RagPipeline | None = None


def get_pipeline() -> RagPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RagPipeline.from_disk()
    return _pipeline


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health() -> dict:
    """Liveness probe — does not touch external APIs."""
    index_ready = (Path(settings.vectorstore_dir) / "index.faiss").exists()
    return {"status": "ok", "index_ready": index_ready}


@app.post("/api/chat")
def chat(req: ChatRequest) -> JSONResponse:
    try:
        result = get_pipeline().query(req.question)
    except FileNotFoundError as exc:
        logger.error("Vector store missing: %s", exc)
        return JSONResponse(status_code=503, content={"error": str(exc)})
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the UI
        logger.exception("Query failed")
        return JSONResponse(status_code=500, content={"error": f"Query failed: {exc}"})

    return JSONResponse(
        content={
            "answer": result.answer,
            "sources": [
                {"source": s.source, "score": s.score, "snippet": s.snippet}
                for s in result.sources
            ],
        }
    )
