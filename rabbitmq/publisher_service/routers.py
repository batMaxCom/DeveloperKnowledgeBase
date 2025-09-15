import logging
from typing import Optional, Literal, Annotated, Union

from fastapi import APIRouter, status, HTTPException, Query, Header

from publisher import RabbitMQProducer
from pydantic import BaseModel

from aio_pika import ExchangeType


router = APIRouter(prefix="/messages", tags=["Messages"])

class PublishResponse(BaseModel):
    status: str
    response: Optional[dict | str] = None

@router.post("/")
async def send_message(
        message: Optional[str] = None,
        routing_key: Optional[str] = "data_requests_queue",
        timeout: Optional[float] = 10.0,
        exchange_type: Literal[
            ExchangeType.DIRECT, ExchangeType.FANOUT, ExchangeType.TOPIC
        ]  = Query(...),
):
    try:
        async with RabbitMQProducer(exchange_type) as client:
            response = await client.publish(
                event=message,
                routing_key=routing_key,
                timeout=timeout
            )
            return PublishResponse(
                status="success",
                response=response
            )
    except TimeoutError:
        logging.warning(f"Timeout publishing message to {routing_key}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="RabbitMQ server did not respond within timeout"
        )
    except Exception as e:
        logging.error(f"Failed to publish message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish message: {str(e)}"
        )
