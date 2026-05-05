import os
import uvicorn

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from backend.routers.auth import router as auth_router
from backend.routers.chat import router as chat_router

app = FastAPI(title="Chatbot API")

app.include_router(auth_router)
app.include_router(chat_router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    favicon_path = os.path.join(current_dir, "favicon.ico")
    return FileResponse(favicon_path)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
