from fastapi import FastAPI
from .Routes.upload import router as upload_router
from .Routes.ask import router as ask_router

from pathlib import Path
from server.services.embeddings.build_index import build_index

VECTOR_DIR = Path("vector_store")

if not VECTOR_DIR.exists():
    build_index()


app = FastAPI()
app.include_router(upload_router, tags=["Upload PDF"], prefix="/api")
app.include_router(ask_router, tags=["Ask Question"], prefix="/api")



