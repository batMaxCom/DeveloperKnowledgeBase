import uvicorn
from fastapi import FastAPI

from routers import websocket_router

app = FastAPI(
    docs_url="/docs"
)

app.include_router(websocket_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )