import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from consumer import consumer_direct, consumer_fanout, consumer_topic


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:  # noqa
    """
    Асинхронный контекстный менеджер, отвечающий за инициализацию и запуск
    необходимых сервисов и подключений при старте приложения FastAPI.
    """
    servers = (
        consumer_direct,
        consumer_fanout,
        consumer_topic,
    )
    [await server.connect() for server in servers]
    tasks = [asyncio.create_task(server.start_consuming()) for server in servers]
    try:
        yield
    except Exception as e:
        logging.exception(f"Exception during app lifespan: {e}")
    finally:
        for task in tasks:
            task.cancel()
        [server.stop() for server in servers]
        await asyncio.gather(*tasks, return_exceptions=True)

app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs"
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )