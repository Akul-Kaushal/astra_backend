from fastapi import FastAPI
from .Routes.upload import router as upload_router
from .Routes.ask import router as ask_router

app = FastAPI()
app.include_router(upload_router, tags=["Upload PDF"], prefix="/api")
app.include_router(ask_router, tags=["Ask Question"], prefix="/api")



