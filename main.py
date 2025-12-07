from fastapi import FastAPI
from backend.Route import root, files, chat


app = FastAPI()

app.include_router(root.router,tags=["Root"])
app.include_router(files.router, prefix="/upload",tags=["Upload PDF"]) 
app.include_router(chat.router, prefix="/chat",tags=["Chat"]) 


